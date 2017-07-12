# *****************************************************************************************************
# * Imports
# *****************************************************************************************************

# Standard Import 
import win32com.client
import configparser
import csv
import fileinput
import multiprocessing
import os
import copy
import numpy.random as rd
import numpy as np
import pandas as pd
import scipy as sp
import scipy.stats as sps
import measurement.measures as conv
from math import *
from gurobipy import *
from statistics import mean
from operator import add, sub, mul
from timeit import default_timer as timer
from deap import base,creator,tools,algorithms

# Class Imports
from VehicleSpecifications import ElectricVehicle
from HouseholdSpecifications import Household
from scipy.stats.stats import spearmanr
from unittest.test.testmock.testpatch import something
from copy import deepcopy

# *****************************************************************************************************
# * Utility Functions
# *****************************************************************************************************

# READING
def read_floatseries(filename):
    with open(filename) as file:
        data = [float(line) for line in file]
    return data

def read_intseries(filename):
    with open(filename) as file:
        data = [int(line) for line in file]
    return data

def merge_timeseries(x,y):
    z = []
    for i in range(num_slots):
        if i<dayswitch_slot:
            z.append(x[start_slot+i])
        else:
            z.append(y[i-dayswitch_slot])
    return z

# UNCERTAINTY
def get_rednoise(r,s,max_shift):
    rednoise = []
    shift = rd.randint(-max_shift,max_shift)
    for i in range(num_slots):
        w = sps.norm.rvs(0,s)
        if i == 0:
            x = w
        else:
            x = r*x + sqrt(1-r**2) * w
        rednoise.append(x)
    return rednoise

# NETWORK    
def updateLoad(ts,id):
    dmd_dss = str(ts).replace(',', '').replace('[', '').replace(']', '')
    DSSText.Command = "Edit Loadshape.Shape_"+str(id)+" mult=("+dmd_dss+")"
    DSSText.Command = "Edit Load.LOAD"+str(id)+" daily=Shape_"+str(id)

def solvePowerFlow():
    DSSText.Command = "reset"
    DSSText.Command = "set year=2"
    time = timer()
    DSSSolution.Solve()
    DSSMonitors.SaveAll

def getVolts():
    volts = []
    for i in range(num_households):
        DSSMonitors.Name = "VI_MON"+str(i+1)
        volts.append(list(DSSMonitors.Channel(1)))
        households[i].voltages = volts[i]
    return volts

def getLoadings():
    loadings = []
    for i in range(num_linerecords): # TODO if I only consider the first line, reasonable assumption
        DSSMonitors.Name = "LINE"+str(i+1)+"_VI_vs_Time"    
        DSSText.Command = "export monitor LINE"+str(i+1)+"_VI_vs_Time"      
        loadings.append( [ list(DSSMonitors.Channel(7)), list(DSSMonitors.Channel(9)), list(DSSMonitors.Channel(11)) ] )
    return loadings

def getSensitivities():
    v_matrix = []
    s_matrix = []
    DSSText.Command = "set mode=snap year=0"
    
    DSSText.Command = "reset"
    DSSSolution.Solve()
    DSSMonitors.SaveAll
    DSSText.Command = "sample"
    for i in range(num_households):
        DSSText.Command = "export monitor VI_MON"+str(i+1)
   
    # line loadings sensitivity
    DSSText.Command = "export currents LVTest_Loadings.csv"
    df_lines = pd.read_csv('LVTest_Loadings.csv', sep=',',skiprows=2,header=None,nrows=num_linerecords,usecols=[1,3,5])
    basecase_loadings = [df_lines[1].tolist(), df_lines[3].tolist(), df_lines[5].tolist()]
    
    # TODO transformer p.r.n.
    #DSSText.Command = "export powers"
    #df_tx = pd.read_csv('LVTest_EXP_POWERS.csv', sep=',',skiprows=907,header=None,nrows=1,usecols=[1,3,5])
    
    basecase_volts = []
    for i in range(num_households):
        DSSMonitors.Name = "VI_MON"+str(i+1)
        basecase_volts.append(DSSMonitors.Channel(1)[0])
        
    for i in range(num_households):
        
        print(">> @Init: Get sensitivity for load change at household "+str(i+1))
        
        if i == 0:
            DSSText.Command = "Edit Load.LOAD"+str(i+1)+" kW=3"
        else:
            DSSText.Command = "Edit Load.LOAD"+str(i+1)+" kW=3"
            DSSText.Command = "Edit Load.LOAD"+str(i)+" kW=2"
        
        DSSText.Command = "reset"
        DSSSolution.Solve()
        DSSMonitors.SaveAll
        DSSText.Command = "sample"
        for i in range(num_households):
            DSSText.Command = "export monitor VI_MON"+str(i+1)
        
        DSSText.Command = "export currents LVTest_Loadings.csv"
        df_lines = pd.read_csv('LVTest_Loadings.csv', sep=',',skiprows=2,header=None,nrows=num_linerecords,usecols=[1,3,5])
        newcase_loadings = [df_lines[1].tolist(), df_lines[3].tolist(), df_lines[5].tolist()]
        
        newcase_volts = []
        for i in range(num_households):
            DSSMonitors.Name = "VI_MON"+str(i+1)
            newcase_volts.append(DSSMonitors.Channel(1)[0])
            
        delta_volts = list(map(sub,newcase_volts,basecase_volts))
        delta_loadings = [list(map(sub,newcase_loadings[i],basecase_loadings[i])) for i in range(3)]
        v_matrix.append(delta_volts)
        s_matrix.append(delta_loadings)
        
    return np.asarray(v_matrix), np.asarray(s_matrix)

# CONTROLLER
def chargeAsFastAsPossible():
    schedules = np.zeros((num_households,num_slots))
    targetSOC = cfg.getfloat("electric_vehicles","targetSOC")
    for ev in evs:
        batterySOC = ev.batterySOC_simulated
        t = 0
        while not batterySOC == (targetSOC*ev.capacity):
            remainingEnergyDemand = targetSOC*ev.capacity-batterySOC
            chargingrate_need = remainingEnergyDemand/(ev.charging_efficiency*conv.Time(min=resolution).hr)
            chargingrate = ev.availability_simulated[t]*min(ev.chargingrate_max, chargingrate_need)
            schedules[ev.position-1][t] = chargingrate
            batterySOC+=(chargingrate*ev.charging_efficiency*conv.Time(min=resolution).hr)
            t+=1
            if t == num_slots:
                break
        ev.schedule = schedules[ev.position-1].tolist()
    return schedules

# *****************************************************************************************************
# * Optimisation Functions
# *****************************************************************************************************

# TODO Gurobi!
def runLinearProgram():
    
    try:
        # Create a new model
        m = Model()

        # Create variables
        x = m.addVars(num_households,num_slots, ub=chargingrate_max)  

        # Set objective
        coeff = [price_ts[i%num_slots]*conv.Time(min=resolution).hr for i in range(num_households*num_slots)]
        vars = [x[i,j] for i in range(num_households) for j in range(num_slots)]
        
        if cfg.getboolean("general", "regulation_service"):
            y = m.addVars(num_households,num_slots,vtype=GRB.BINARY)
            m.update()
            revenue = (-1)*charging_efficiency*chargingrate_max*reg_price*y.sum()
            m.setObjective(LinExpr(coeff,vars)+LinExpr(revenue), GRB.MINIMIZE)
        else:
            m.setObjective(LinExpr(coeff,vars), GRB.MINIMIZE)
    
        # Add electric vehicle constraints:
        for i in range(num_households):
            if households[i].ev != None:
                for j in range(num_slots):
                    m.addConstr((1-households[i].ev.availability_forecast[j])*x[i,j]==0)
                    if j >= 1:
                        m.addConstr((households[i].ev.availability_forecast[j]*households[i].ev.availability_forecast[j-1])*(x[i,j]-x[i,j-1]) >= -change_max)
                        m.addConstr((households[i].ev.availability_forecast[j]*households[i].ev.availability_forecast[j-1])*(x[i,j]-x[i,j-1]) <= change_max)
                m.addConstr(households[i].ev.batterySOC_forecast + charging_efficiency*conv.Time(min=resolution).hr*x.sum(i,'*') == households[i].ev.capacity)
                if cfg.getboolean("general", "regulation_service"):
                    expr = [x[i,k] for k in range(j+1)]
                    m.addConstr(y[i,j]*(households[i].ev.batterySOC_forecast+charging_efficiency*conv.Time(min=resolution).hr*LinExpr([1 for _ in range(len(expr))],expr)) >= reg_threshold*households[i].ev.capacity)
        
        # Add technical constraints:
        for i in range(num_households):
                for j in range(num_slots):
                    m.addConstr(v_init[i][j] + LinExpr(v_sensitivity.T[i],[x[k,j] for k in range(num_households)]) >= voltage_min*base_volt_perphase)
        
        if cfg.getboolean("general", "overload_constraints"):
            rating = 165 # TODO automatic rating reading
            for i in range(num_linerecords):
                for t in range(num_slots):
                    for p in range(3):
                        stv = [s_sensitivity[k,p,i] for k in range(num_households)]
                        var = [x[k,t] for k in range(num_households)]
                        m.addConstr(s_init[i][p][t] + LinExpr(stv, var) <= rating)
        
        #m.write("../log/linearprogram.lp")
        m.optimize()
        print('Obj: %g' % m.objVal)
        
        #translate to schedule
        schedules = np.zeros((num_households,num_slots))
        for i in range(num_households):
            for j in range(num_slots):
                schedules[i][j] = x[i,j].X
            if households[i].ev != None:
                households[i].ev.schedule = schedules[i]
        return schedules
    
    except GurobiError as e:
        print('Error code ' + str(e.errno) + ": " + str(e))
    
    except AttributeError:
        print('Encountered an attribute error')
    
    return 0

# priceGREEDY
def runPriceGreedy():
    schedules = np.zeros((num_households,num_slots))
    
    # sort price time series
    if not cfg.get("uncertainty_mitigation","availability") == "penalty":
        price_ts_opt = np.array(price_ts)
        order_prices = np.argsort(price_ts_opt)
    
    for ev in evs:
        
        if cfg.get("uncertainty_mitigation","availability") == "penalty":
            p_av = ev.availability_probability
            penalty = cfg.getfloat("uncertainty_mitigation", "penalty")
            price_ts_opt = []
            for i in range(num_slots):
                price = p_av[i] * price_ts[i] + (1-p_av[i]) * penalty
                price_ts_opt.append(price)
            order_prices = np.argsort(price_ts_opt)
        
        t = 0
        currentSOC = ev.batterySOC_forecast
        while not currentSOC == (targetSOC*ev.capacity):
            remainingEnergyDemand = targetSOC*ev.capacity-currentSOC
            chargingrate_need = remainingEnergyDemand/(ev.charging_efficiency*conv.Time(min=resolution).hr)
            chargingrate = ev.availability_forecast[order_prices[t]]*min(ev.chargingrate_max, chargingrate_need)
            schedules[ev.position][order_prices[t]] = chargingrate
            currentSOC+=(chargingrate*ev.charging_efficiency*conv.Time(min=resolution).hr)
            t+=1
            if t == num_slots:
                break
        ev.schedule = schedules[ev.position].tolist()
    
    return schedules

# networkGREEDY
def runNetworkGreedy(urgency_mode):
    schedules = np.zeros((num_households,num_slots))
    
    # sort price time series
    if not cfg.get("uncertainty_mitigation","availability") == "penalty":
        price_ts_opt = np.array(price_ts)
        order_prices = np.argsort(price_ts_opt)
    
    if urgency_mode == "distance":
        # only works if all households have EV TODO
        alldistances = DSSCircuit.AllNodeDistancesByPhase(1)
        load_locations = read_intseries("../network_details/LoadLocations.txt")
        distances = np.zeros(num_households)
        for i in range(len(load_locations)):
            distances[i] = alldistances[load_locations[i]]
        order_urgency = np.argsort(distances)
    elif urgency_mode == "manual":
        # only works if all households have EV TODO
        order_urgency = np.asarray(read_intseries("../parameters/manual_order.txt")) - 1
    elif urgency_mode == "arrival":
        arrival_slots = np.zeros(num_evs)
        for i in range(num_evs):
            arrival_slots[i] = evs[i].availability_simulated.index(1)
            evs[i].batterySOC_forecast = evs[i].batterySOC_simulated
            j=0
            while not evs[i].availability_simulated[j] == evs[i].availability_forecast[j]:
                evs[i].availability_forecast[j] = evs[i].availability_simulated[j]
                j+=1
        order_urgency = np.argsort(arrival_slots)
    elif urgency_mode == "soc":
        # prioritise electric vehicles according to SOC and availability period
        urgency = np.zeros(num_evs)
        deg_freedom = np.zeros(num_evs)
        arrivalSOCs = np.zeros(num_evs)
        for k in range(num_evs):
            arrivalSOCs[k] = evs[k].batterySOC_forecast
            deg_freedom[k] = sum(evs[k].availability_forecast)
            urgency[k] = evs[k].batterySOC_forecast*sum(evs[k].availability_forecast)      
        order_urgency = np.argsort(urgency)
    else:
        urgency_mode = [i for i in range(num_evs)]
    print(order_urgency)
    
    for k in range(num_evs):
        
        if cfg.get("uncertainty_mitigation","availability") == "penalty":
            p_av = evs[k].availability_probability
            penalty = cfg.getfloat("uncertainty_mitigation", "penalty")
            price_ts_opt = []
            for i in range(num_slots):
                price = p_av[i] * price_ts[i] + (1-p_av[i]) * penalty
                price_ts_opt.append(price)
            print(spearmanr(price_ts, price_ts_opt))
            order_prices = np.argsort(price_ts_opt)
        
        max_rate = [chargingrate_max for i in range(num_slots)]

        # select electric vehicle
        if urgency_mode == "dist" or urgency_mode == "manual":
            ev = households[order_urgency[k]].ev
        else:
            ev_id = order_urgency[k]
            ev = evs[ev_id]
        hd_id = ev.position
        print("Schedule "+str(k+1)+"th vehicle at household "+str(hd_id)) 
        
        # repeat schedule proposals until feasible solution acquired (with forecast data)
        feasible = False
        while not feasible:
            
            # calculate greedy schedule proposal
            t = 0
            
            currentSOC = ev.batterySOC_forecast
            while not currentSOC == (targetSOC*ev.capacity):
                pr_id = order_prices[t]
                remainingEnergyDemand = targetSOC*ev.capacity-currentSOC
                chargingrate_need = remainingEnergyDemand/(ev.charging_efficiency*conv.Time(min=resolution).hr)
                chargingrate = min(max_rate[pr_id],ev.availability_forecast[pr_id]*min(ev.chargingrate_max, chargingrate_need))
                schedules[ev.position][pr_id] = chargingrate
                currentSOC+=(chargingrate*ev.charging_efficiency*conv.Time(min=resolution).hr)
                t+=1
                if t == num_slots:
                    break
        
            print("-> Required "+str(t)+" slots to complete charge")  
            
            # test proposed schedule for voltage problems
            if not cfg.getboolean("general", "network_sensitivity"):
                newload = list(map(add,households[hd_id].demandForecast, schedules[hd_id]))
                updateLoad(newload,hd_id+1)
                solvePowerFlow()
                slot_minvolts = np.zeros(num_slots)
                for i in range(num_slots):
                    slot_minvolts[i] = min(np.asarray(getVolts()).T[i])
                
                if cfg.getboolean("general", "overload_constraints"):
                    slot_overloads = np.unique(np.genfromtxt("../network_details/LVTest/DI_yr_2/DI_Overloads.CSV",delimiter=',',skip_header=1,usecols=(0,))) / conv.Time(min=resolution).hr -1
                    slot_overloads = [int(i) for i in slot_overloads.tolist()]
                else:
                    slot_overloads = []
            else:
                approx_volts = np.asarray(copy.deepcopy(v_init))
                for t in range(num_slots):
                     for i in range(num_households):
                         for j in range(num_households):
                             approx_volts[i][t] += v_sensitivity[j][i]*schedules[j][t]
                slot_minvolts = np.zeros(num_slots)
                for i in range(num_slots):
                    slot_minvolts[i] = min(approx_volts.T[i])
                
                if cfg.getboolean("general", "overload_constraints"):
                    approx_loadings = np.asarray(copy.deepcopy(s_init))
                    for t in range(num_slots):
                        for i in range(num_linerecords):
                            for j in range(num_households):
                                for p in range(3):
                                    approx_loadings[i][p][t] += s_sensitivity[j][p][i]*schedules[j][t]
                    approx_loadings = np.max(approx_loadings,axis=1)
                    slot_overloads = []
                    rating = 165 # TODO automatic line rating reading
                    for t in range(num_slots):
                        for i in range(num_linerecords):
                            if approx_loadings[i][t] > rating:
                                slot_overloads.append(t)
                    slot_overloads = list(set(slot_overloads))
                else:
                    slot_overloads = []
                
        
            if min(slot_minvolts) < voltage_min*base_volt_perphase or len(slot_overloads) > 0:
                
                if min(slot_minvolts) < voltage_min*base_volt_perphase and len(slot_overloads) > 0:
                    print("-> Voltage violation with "+format(min(slot_minvolts)/base_volt_perphase, ".3f")+" and overload at slot "+str(slot_overloads)+". Enter mitigation routine.")
                elif min(slot_minvolts) < voltage_min*base_volt_perphase:
                    print("-> Only voltage violation with "+format(min(slot_minvolts)/base_volt_perphase, ".3f")+". Enter mitigation routine.")
                elif len(slot_overloads) > 0:
                    print("-> Only overload at slot "+str(slot_overloads))
                
                # set price to infinity, update order of price time series
                indices = [l for l,v in enumerate(slot_minvolts < voltage_min*base_volt_perphase) if v]
                indices.extend(slot_overloads)
                indices = list(set(indices))
                block_indices = []
                for i in indices:
                    max_rate[i] -= cfg.getfloat('networkGREEDY', 'decrement')
                    print("-> Reduce max charging rate at ["+str(i)+"] to "+format(max(0,max_rate[i]), ".3f")+" kW.")
                    if max_rate[i] <= 0:
                        block_indices.append(i)
                for bi in block_indices:
                    price_ts_opt[bi] = inf
                    order_prices = np.argsort(price_ts_opt)
                    for i in range(num_slots):
                        schedules[hd_id][i] = 0.0
                if len(block_indices) != 0:
                    print("-> Forbid further loads in slots "+str(block_indices))
            else:
                print("-> No violations. Continue with proposed schedule.")
                feasible = True

        ev.schedule = schedules[hd_id].tolist()   
        
    return schedules

# PSO
def runOptParticleSwarm():
    
    # TODO parametrisation
    
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Particle", list, fitness=creator.FitnessMin, speed=None, smin=None, smax=None, best=None)
    creator.create("Swarm", list, gbest=None, gbestfit=creator.FitnessMin)
    
    IND_SIZE = num_slots * num_evs
    POP_SIZE = 30
    
    toolbox = base.Toolbox()
    toolbox.register("particle", generate, size=IND_SIZE, pmin=0.0, pmax=chargingrate_max, smin=-1.0, smax=1.0)
    toolbox.register("swarm", tools.initRepeat, creator.Swarm, toolbox.particle)
    toolbox.register("update", updateParticle, phi1=2.0, phi2=2.0)
    toolbox.register("evaluate", evaluate)
    toolbox.decorate("evaluate", tools.DeltaPenalty(feasible, 0.0, distance))
    
    pop = toolbox.swarm(n=POP_SIZE)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    logbook = tools.Logbook()
    logbook.header = ["gen", "evals"] + stats.fields

    GEN = 1
    best = None

    for g in range(GEN):
        for part in pop:
            part.fitness.values = toolbox.evaluate(part)
            if not part.best or part.best.fitness < part.fitness:
                part.best = creator.Particle(part)
                part.best.fitness.values = part.fitness.values
            if not best or best.fitness < part.fitness:
                best = creator.Particle(part)
                best.fitness.values = part.fitness.values
        for part in pop:
            toolbox.update(part, best)

        # Gather all the fitnesses in one list and print the stats
        logbook.record(gen=g, evals=len(pop), **stats.compile(pop))
        print(logbook.stream)
    
    ev_schedules = np.asarray(best).reshape((num_evs,num_slots))
    schedules = np.zeros((num_households,num_slots)).tolist()
    
    for i in range(num_evs):
        schedules[evs[i].position] = ev_schedules[i].tolist()
        evs[i].schedule = schedules[evs[i].position]
        
    return schedules

# GA
def runOptGenetic():
    
    # TODO parametrisation
    
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)
    
    IND_SIZE = num_slots * num_evs
    POP_SIZE = 30
    
    toolbox = base.Toolbox()
    toolbox.register("attr_float", rd.random) # TODO heuristic init
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=IND_SIZE)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual, n=POP_SIZE)
    toolbox.register("evaluate", evaluate)
    toolbox.decorate("evaluate", tools.DeltaPenalty(feasible, 0.0, distance))
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.5, indpb=0.5)
    toolbox.register("select", tools.selTournament, tournsize=3)
   
    stats = tools.Statistics(key=lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)
   
    hof = tools.HallOfFame(1)
    population = toolbox.population()

# if no of-the-shelf algorithm used...
#     fits = toolbox.map(toolbox.evaluate, population)
#     for fit, ind in zip(fits, population):
#             ind.fitness.values = fit
    
    population, logbook = algorithms.eaSimple(population, toolbox, cxpb=0.5, mutpb=0.3, ngen=5, stats=stats, verbose=True, halloffame=hof)
    
    sorted_pop = sorted(population, key=lambda ind: ind.fitness)
    
    ev_schedules = np.asarray(best).reshape((num_evs,num_slots))
    schedules = np.zeros((num_households,num_slots)).tolist()
    
    for i in range(num_evs):
        schedules[evs[i].position] = ev_schedules[i].tolist()
        evs[i].schedule = schedules[evs[i].position]
        
    return schedules

# *****************************************************************************************************
# * Algorithm Side Functions
# *****************************************************************************************************

def generate(size, pmin, pmax, smin, smax):
    part = creator.Particle(rd.uniform(pmin, pmax) for _ in range(size)) 
    part.speed = [rd.uniform(smin, smax) for _ in range(size)]
    part.smin = smin
    part.smax = smax
    return part

def updateParticle(part, best, phi1, phi2):
    u1 = (rd.uniform(0, phi1) for _ in range(len(part)))
    u2 = (rd.uniform(0, phi2) for _ in range(len(part)))
    v_u1 = map(mul, u1, map(sub, part.best, part))
    v_u2 = map(mul, u2, map(sub, best, part))
    part.speed = list(map(add, part.speed, map(add, v_u1, v_u2)))
    for i, speed in enumerate(part.speed):
        if speed < part.smin:
            part.speed[i] = part.smin
        elif speed > part.smax:
            part.speed[i] = part.smax
    part[:] = list(map(add, part, part.speed))

# *****************************************************************************************************
# * Evaluation Functions
# *****************************************************************************************************

def evaluate(individual):
    fitness = 0
    for k in range(num_evs):
        for t in range(num_slots):
            fitness+=individual[k*num_slots+t]*price_ts[t]*conv.Time(min=duration).hr
            # Regulation Service
            # TODO
    return fitness, # must be tuple

def feasible(individual):
    feasible = True
    for k in range(num_evs):
        power_drawn = 0.0
        for t in range(num_slots):
            # charging rate bounds
            if 0.0 > individual[k*num_slots+t] > chargingrate_max:
                feasible = False
            # availability bounds
            if (1-evs[k].availability_forecast[t])*individual[k*num_slots+t] != 0.0:
                feasible = False
            power_drawn += individual[k*num_slots+t]
        # full battery SOC bounds
        if targetSOC*evs[k].capacity > evs[k].batterySOC_forecast + evs[k].charging_efficiency * conv.Time(min=resolution).hr * power_drawn > evs[k].capacity:
            feasible = False
    
    # change of charging rate bound
    # TODO
    
    # regulation service bound
    # TODO

    # technical bounds
    ev_schedules = [individual[i:i+num_slots] for i in range(0, len(individual), num_slots)]
    for k in range(num_evs):
        hd_id = evs[k].position       
        newload = list(map(add,households[hd_id].demandForecast, ev_schedules[k]))
        updateLoad(newload,hd_id+1)
    solvePowerFlow()
    slot_minvolts = np.zeros(num_slots)
    for i in range(num_slots):
        slot_minvolts[i] = min(np.asarray(getVolts()).T[i])
    if min(slot_minvolts) < voltage_min*base_volt_perphase:
        feasible = False
    return feasible

def distance(individual):
    return 0.0 # TODO

# *****************************************************************************************************
# * Evaluation after Simulation or Optimisation
# *****************************************************************************************************
def evaluateResults(code):
    
    print("-------------------------------------------------")
    print(">> @Eval: Starting "+code+" evaluation and fill logs.")
    
    # schedule reality adjustment
    if code == "sim":
        for j in range(num_households):
            if households[j].ev != None:
                currentSOC = households[j].ev.batterySOC_simulated
                forced_stop = False
                for i in range(num_slots):
                    schedules[j][i] = schedules[j][i]*households[j].ev.availability_simulated[i]
                    currentSOC += (schedules[j][i]*ev.charging_efficiency*conv.Time(min=resolution).hr)
                    if forced_stop:
                        schedules[j][i] = 0.0
                    elif currentSOC > households[j].ev.capacity:
                        schedules[j][i] = max(0,households[j].ev.capacity - currentSOC + schedules[j][i]*ev.charging_efficiency*conv.Time(min=resolution).hr)/(ev.charging_efficiency*conv.Time(min=resolution).hr)
                        forced_stop = True
                households[j].ev.schedule = schedules[j]
    else:
        if cfg.getboolean("general","network_sensitivity"):
            
            # voltages
            approx_volts = np.asarray(copy.deepcopy(v_init))
            for t in range(num_slots):
                for i in range(num_households):
                    for j in range(num_households):
                        approx_volts[i][t] += v_sensitivity[j][i]*schedules[j][t]
            np.savetxt("../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_ApproxVoltages.csv", np.asarray(approx_volts), delimiter=",")             
            
            # approximate line loadings
            approx_loadings = np.asarray(copy.deepcopy(s_init))
            for t in range(num_slots):
                for i in range(num_linerecords):
                    for j in range(num_households):
                        for p in range(3):
                            approx_loadings[i][p][t] += s_sensitivity[j][p][i]*schedules[j][t]
            approx_loadings = np.max(approx_loadings,axis=1)
            np.savetxt("../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_ApproxLoadings.csv", approx_loadings, delimiter=",")             

    # reparation controller
    # TODO
    
    # include schedule in residential net load
    netloads = []
    for i in range(num_households):
        if code == "opt":
            netload = list(map(add,households[i].demandForecast, schedules[i]))
        elif code == "sim":
            netload = list(map(add,households[i].demandSimulated, schedules[i]))
        else:
            exit(1)
        netloads.append(netload)
        updateLoad(netload,i+1)
    
    solvePowerFlow()
    household_voltages = getVolts()
    eval_start = timer()
    
    # actual loadings log
    actual_loadings = np.max(np.asarray(getLoadings()),axis=1)
    np.savetxt("../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_ActualLoadings.csv", actual_loadings, delimiter=",")             
    
    # WRITE HOUSEHOLD AGGREGATE LOG
    filename = "../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_HouseholdAggregate.csv"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    log_hd = open(filename, 'w', newline='')
    hdlog_writer = csv.writer(log_hd,delimiter=',')
    hdlog_writer.writerow( ( 'id', 'inhabitants', 'withEV', 'chCostTotal', 'regRevTotal', 'netChCostTotal','resCostTotal','totalCostTotal',\
                          'netDemandTotal', 'evDemandTotal', 'resDemandTotal', 'pvGenTotal', 'minVoltageV','minVoltagePU' ) )
    
    # instantiate arrays for post-calculations
    chCost = np.zeros((num_households,num_slots))
    netChCost = np.zeros((num_households,num_slots))
    totalCost = np.zeros((num_households,num_slots))
    resCost = np.zeros((num_households,num_slots))
    regAv  = np.zeros((num_households,num_slots))
    regRev = np.zeros((num_households,num_slots))
    eCharged = np.zeros((num_households,num_slots))
    batterySOC = np.zeros((num_households,num_slots))
    av = np.zeros((num_households,num_slots))
    prob_av = np.zeros((num_households,num_slots))
    resDemand = []
    
    j = 0
    for hd in households:
        
        if code == "sim":
            eva_demand = hd.demandSimulated
            if hd.ev is None:
                eva_availability = list(np.zeros(num_slots))
                eva_batterySOC = list(np.zeros(num_slots))
            else:
                eva_availability = hd.ev.availability_simulated
                eva_batterySOC = hd.ev.batterySOC_simulated
            eva_price = price_ts_sim
        elif code == "opt":
            eva_demand = hd.demandForecast
            if hd.ev is None:
                eva_availability = list(np.zeros(num_slots))
                eva_batterySOC = list(np.zeros(num_slots))
            else:
                eva_availability = hd.ev.availability_forecast
                eva_batterySOC = hd.ev.batterySOC_forecast
            eva_price = price_ts
        else:
            print("Choose 'opt' or 'sim' for evaluation mode")
            exit(1)
         
        resDemand.append(eva_demand)
         
        for i in range(num_slots):
            if hd.ev is None:
                av[j][i] = 0
                prob_av[j][i] = 0
                eCharged[j][i] = 0
                chCost[j][i] = 0
                batterySOC[j][i] = 0
            else:
                av[j][i] = eva_availability[i]
                prob_av[j][i] = hd.ev.availability_probability[i]
                eCharged[j][i] = hd.ev.schedule[i]*hd.ev.charging_efficiency*conv.Time(min=resolution).hr
                chCost[j][i] = hd.ev.schedule[i]*conv.Time(min=resolution).hr*eva_price[i]/100
                if i == 0:
                    #batterySOC[j][i] = av[j][i]*(eva_batterySOC+eCharged[j][i])
                    batterySOC[j][i] = (eva_batterySOC+eCharged[j][i])
                else:
                    #batterySOC[j][i] = av[j][i]*(max(eva_batterySOC+eCharged[j][i],batterySOC[j][i-1]+eCharged[j][i]))
                    batterySOC[j][i] = (max(eva_batterySOC+eCharged[j][i],batterySOC[j][i-1]+eCharged[j][i]))
            regAv[j][i] = 0 
            regRev[j][i] = 0
            netChCost[j][i] = chCost[j][i]-regRev[j][i] 
            resCost[j][i] = eva_demand[i]*conv.Time(min=resolution).hr*eva_price[i]/100
            totalCost[j][i] = resCost[j][i]+netChCost[j][i]
    
         
        # WRITE individual household solutions to CSV
        filename = "../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_household"+format(j+1,"02d")+".csv"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', newline='') as f:
            try:
                solution_writer = csv.writer(f,delimiter=',')
                solution_writer.writerow( ( 'slot', 'netLoad', 'resLoad', 'pvGen','evSchedule',\
                                   'evAvailability', 'regAvailability', 'energyCharged','batterySOC',\
                                   'voltageV','voltagePU', 'elPrice', 'chCost', 'regRev', 'netChCost','resCost','totalCost' ) )
                for i in range(num_slots):
                    solution_writer.writerow( ( (i+1), netloads[j][i], eva_demand[i], 0, schedules[j][i],\
                                        av[j][i], 0, eCharged[j][i],batterySOC[j][i], hd.voltages[i], hd.voltages[i]/base_volt_perphase, eva_price[i],chCost[j][i],\
                                        regRev[j][i],netChCost[j][i],resCost[j][i],totalCost[j][i]) )
            finally:
                f.close()
                 
        hdlog_writer.writerow( ( (j+1), hd.inhabitants, max(av[j]), sum(chCost[j]), sum(regRev[j]), sum(netChCost[j]), sum(resCost[j]),\
                              sum(totalCost[j]), conv.Time(min=duration).hr*sum(netloads[j])/len(netloads[j]),\
                              conv.Time(min=duration).hr*sum(schedules[j])/len(schedules[j]),\
                              conv.Time(min=duration).hr*sum(eva_demand)/len(eva_demand), 0, min(hd.voltages), min(hd.voltages)/base_volt_perphase ) )
        j+=1
    
    log_hd.close()
    
    # SLOTWISE AGGREGATE LOG
    filename = "../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_SlotwiseAggregate.csv"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    log_slot = open(filename, 'w', newline='')
    slotlog_writer = csv.writer(log_slot,delimiter=',')
    slotlog_writer.writerow( ( 'slot', 'netLoad', 'resLoad', 'pvGen','evSchedule',\
                       'evAvailability', 'regAvailability', 'batterySOC','batterySOCmin',\
                       'minVoltageV','minVoltagePU', 'elPrice', 'chCost', 'regRev', 'netChCost','resCost','totalCost' ) )
    
    for i in range(num_slots):
        slotlog_writer.writerow( ( (i+1), sum(np.asarray(netloads).T[i]), sum(np.asarray(resDemand).T[i]), 0,\
                                   sum(np.asarray(schedules).T[i]*av.T[i]), sum(av.T[i]),sum(regAv.T[i]),\
                                   sum(batterySOC.T[i])/(num_evs*ev.capacity),min(batterySOC.T[i])/ev.capacity,min(np.asarray(household_voltages).T[i]),\
                                   min(np.asarray(household_voltages).T[i])/base_volt_perphase,eva_price[i],sum(chCost.T[i]),\
                                   sum(regRev.T[i]),sum(netChCost.T[i]),sum(resCost.T[i]),sum(totalCost.T[i]) ) )
    log_slot.close()
    
    # WRITE SOME MORE FILES
    pathname = "../log/iter"+str(mc_iter)
    os.makedirs(os.path.dirname(pathname), exist_ok=True)
    np.savetxt("../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_Voltages.csv", np.asarray(household_voltages), delimiter=",")
    np.savetxt("../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_Schedules.csv", np.asarray(schedules), delimiter=",")
    np.savetxt("../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_NetLoads.csv", np.asarray(netloads), delimiter=",")
    np.savetxt("../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_ResLoads.csv", np.asarray(resDemand), delimiter=",")
    np.savetxt("../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_EVAvailability.csv", np.asarray(av), delimiter=",")
    np.savetxt("../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_NetChCost.csv", np.asarray(netChCost), delimiter=",")
    np.savetxt("../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_TotalCost.csv", np.asarray(totalCost), delimiter=",")
    np.savetxt("../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_ResCost.csv", np.asarray(resCost), delimiter=",")
    np.savetxt("../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_BatterySOC.csv", np.asarray(batterySOC), delimiter=",")
    np.savetxt("../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_RegAvailability.csv", np.asarray(regAv), delimiter=",")
    np.savetxt("../log/iter"+str(mc_iter)+"/"+code+"/"+code+"Results_PAvailability.csv", np.asarray(prob_av), delimiter=",")

    eval_end = timer()
    eval_time = eval_end - eval_start
    print(">> @Eval: Evaluation completed after "+format(eval_time, ".3f")+" seconds.")
    
    # WRITE OPENDSS EXPORT OFFERS
    # DSSText.Command = "export voltages"
    # DSSText.Command = "export seqvoltages"
    # DSSText.Command = "export powers"
    # DSSText.Command = "export seqpowers"
    # DSSText.Command = "export loads"
    # DSSText.Command = "export summary"
    
    # TODO extend for MC analysis
    return sum(map(sum,netChCost))

# *****************************************************************************************************
# * General Framework Initialisation
# *****************************************************************************************************
print(">>> Programme started.")
print("-------------------------------------------------")

# Administrative
rd.seed(196273724)
np.set_printoptions(threshold=np.nan)
print(">> @Init: Utilities defined.")

# *****************************************************************************************************
# * Read Parameters
# *****************************************************************************************************

cfg = configparser.ConfigParser()
cfg.read("../parameters/evalParams.ini")

# assign parameter names
iterations = cfg.getint("general","iterations")
surcharge = cfg.getfloat("market_prices","surcharge")
spread = cfg.getfloat("market_prices","spread")
evpenetration = cfg.getfloat("electric_vehicles","penetration")
start = conv.Time(hr=cfg.getfloat("general","starting")).min 
duration = conv.Time(hr=cfg.getint("general","duration")).min
resolution = cfg.getint("general","resolution")
season = cfg.get("general", "season")
reg_price = cfg.getfloat("market_prices", "regulation_price")
reg_threshold = cfg.getfloat("electric_vehicles","reg_threshold")
targetSOC = cfg.getfloat("electric_vehicles","targetSOC")
chargingrate_max = cfg.getfloat("electric_vehicles","chargingrate_max")
charging_efficiency = cfg.getfloat("electric_vehicles", "charging_efficiency")
change_max = cfg.getfloat("electric_vehicles", "change_max")
voltage_min = cfg.getfloat("network","voltage_min")
loadmultiplier = cfg.getfloat("network","load_multiplier")
urgency_mode = cfg.get("networkGREEDY","urgency_mode")

# calculate further parameters from config
num_slots = int(duration/resolution)
dayswitch_slot = int((duration-start)/resolution) # first slot belonging to new day
start_slot = int(start/resolution)

# non-changeable final parameters
num_households = 55
base_volt_perphase = 230
num_linerecords = 1 # or 905 for all lines

print(">> @Init: Parameters read.")

# *****************************************************************************************************
# * Initialize OpenDSS
# *****************************************************************************************************

# Instantiate the OpenDSS Object
try:
    DSSObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
except:
    print("<< @Init: Unable to start the OpenDSS Engine")
    raise SystemExit

print(">> @Init: OpenDSS engine opened.")

# Set up the Text, Circuit, and Solution Interfaces to manage OpenDSS
DSSText = DSSObj.Text
DSSCircuit = DSSObj.ActiveCircuit
DSSSolution = DSSCircuit.Solution
DSSBus = DSSCircuit.ActiveBus
DSSMonitors = DSSCircuit.Monitors

# Compile and set major parameters
DSSText.Command = r"Compile '..\network_details\Master.dss'"
print(">> @Init: Network instantiated and compiled.")

if cfg.getboolean("general", "network_sensitivity"):     
    v_sensitivity, s_sensitivity = getSensitivities()

# set major parameters
DSSText.Command = "set mode=daily number="+str(num_slots)+" stepsize="+str(resolution)+"m"
for i in range(num_households):
    DSSText.Command = "New Loadshape.Shape_"+str(i+1)
    DSSText.Command = "~ npts="+str(num_slots)
    DSSText.Command = "~ minterval="+str(resolution)
    DSSText.Command = "~ useactual=true"
    
COST = []
for mc_iter in range(1,iterations+1):
    # *****************************************************************************************************
    # * Generate Scenario
    # *****************************************************************************************************
    print("-------------------------------------------------")
    print("SCENARIO " + str(mc_iter) + "/" + str(iterations) + " -- " + format(mc_iter/iterations*100, ".2f") + " %")
    print("-------------------------------------------------")
    
    # assign residential load forecast in network
    households = [Household() for i in range(num_households)]
    counter = 1
    for hd in households:
        hd.day_id_1 = rd.randint(1,hd.id_range)
        demand_ts1 = read_floatseries("../demand_timeseries/loadprofile_"+season+"_inh"+\
                                     str(hd.inhabitants)+"_"+str(resolution)+"min"+format(hd.day_id_1,"03d")+".txt")
        hd.day_id_2 = rd.randint(1,hd.id_range)
        demand_ts2 = read_floatseries("../demand_timeseries/loadprofile_"+season+"_inh"+\
                                     str(hd.inhabitants)+"_"+str(resolution)+"min"+format(hd.day_id_2,"03d")+".txt")
        hd.demandForecast = merge_timeseries(demand_ts1,demand_ts2)
        hd.demandForecast = [x * loadmultiplier for x in hd.demandForecast]
        hd.demandSimulated = copy.deepcopy(hd.demandForecast)
        if cfg.get("uncertainty_mitigation", "demand") == "norm":
            # TODO investigate further options - 
            req_demand_certainty = cfg.getfloat("uncertainty_mitigation", "req_demand_certainty")
            dem_security_margin = [sps.norm.ppf(req_demand_certainty, loc=0, scale=0.3) for _ in range(num_slots)] # TODO set parameters properly
            hd.demandForecast = list(map(add,hd.demandForecast,dem_security_margin))
        updateLoad(hd.demandForecast,counter)
        counter+=1
    print(">> @Scen: "+str(num_households)+" households initialised and demand forecasts generated.")
    
    # assign PV generation forecast in network
    # TODO
    
    # assign EV behaviour in network
    num_evs = round(evpenetration * num_households)
    deck = list(range(num_households))
    rd.shuffle(deck)
    evs = []
    for i in range(num_evs):
        ev_household_id = deck.pop()
        households[ev_household_id].ev = ElectricVehicle(cfg,ev_household_id)
        evs.append(households[ev_household_id].ev)
    
    print(">> @Scen: "+str(len(evs))+"/" +str(num_households)+" possible vehicles initialised and located.")
    
    # generate EV availability and battery state of charge forecast
    for ev in evs:
        ev.generateAvailabilityForecast()
        ev.generateAvailabilityProbability()
        ev.generateBatterySOCForecast()
        
    print(">> @Scen: Vehicle availability and battery SOC forecasts generated.")
    
    # generate electricity price forecast
    day_id = rd.randint(0,999)
    price_ts1 = read_floatseries("../price_timeseries/"+str(resolution)+"min/priceprofile_ukpx_"+str(resolution)+"min"+format(day_id,"04d")+".txt")
    price_ts2 = read_floatseries("../price_timeseries/"+str(resolution)+"min/priceprofile_ukpx_"+str(resolution)+"min"+format(day_id+1,"04d")+".txt")
    price_ts = merge_timeseries(price_ts1, price_ts2)
    mean_price = mean(price_ts)
    price_ts = [((item - mean_price) * spread + mean_price + surcharge) for item in price_ts]
    print(">> @Scen: Electricity market prices forecast generated.")
    
    #DSSText.Command = "set year=1"
    #DSSSolution.Solve()
    
    solvePowerFlow()
    v_init = getVolts()
    s_init = getLoadings()
    
    # *****************************************************************************************************
    # * Run Simulation
    # *****************************************************************************************************
    print("-------------------------------------------------")
    
    # generate actual EV arrival/departure times
    unc_ev_arr = cfg.getboolean("uncertainty","unc_ev_arr")
    unc_ev_dep = cfg.getboolean("uncertainty","unc_ev_dep")
    if unc_ev_arr or unc_ev_dep:
        for ev in evs:
            ev.simulateAvailability(unc_ev_arr, unc_ev_dep)
        print(">> @Sim: Vehicle arrival/departure uncertainty realised.")
    else:
        for ev in evs:
            ev.availability_simulated = ev.availability_forecast
        print(">> @Sim: Vehicle arrival/departure uncertainty not realised.")
    
    # generate actual EV mileage behaviour
    if cfg.getboolean("uncertainty","unc_ev_soc"):
        for ev in evs:
            ev.simulateBatterySOC()
        print(">> @Sim: Vehicle SOC uncertainty realised.")
    else:
        for ev in evs:
            ev.batterySOC_simulated = ev.batterySOC_forecast
        print(">> @Sim: Vehicle SOC uncertainty not realised.")
    
    # generate actual demand behaviour
    if cfg.getboolean("uncertainty", "unc_dem"):
        for hd in households:
            error = get_rednoise(0.8, 0.3, 4) #  TODO proper demand uncertainty
            hd.demandSimulated =  list(map(add,hd.demandSimulated,error))
        print(">> @Sim: Demand uncertainty realised.")
    else:
        print(">> @Sim: Demand uncertainty not realised.")
    
    # generate actual electricity prices    
    if cfg.getboolean("uncertainty", "unc_pri"):
        price_ts_sim = np.zeros(num_slots)
        error = get_rednoise(0.9, 1, 2) # TODO set properly
        price_ts_sim = list(map(add,price_ts,error))
        print(">> @Sim: Price uncertainty realised.")
    else:
        price_ts_sim = list(price_ts)
        print(">> @Sim: Price uncertainty not realised.")
    
    # TEST TODO
    print(spearmanr(price_ts, price_ts_sim))
    
    # *****************************************************************************************************
    # * Run Optimisation
    # *****************************************************************************************************
    print("-------------------------------------------------")
    
    alg = cfg.get("general","algorithm") 
    print(">> @Opt: "+alg+" selected as optimisation algorithm.")
    start = timer()
    
    if alg == "priceGREEDY":
        schedules = runPriceGreedy()
    elif alg == "networkGREEDY":
        schedules = runNetworkGreedy(urgency_mode)
    elif alg == "GA":
        schedules = runOptGenetic()
    elif alg == "PSO":
        schedules = runOptParticleSwarm()
    elif alg == "LP":
        schedules = runLinearProgram()
    else:
        schedules = chargeAsFastAsPossible()
    
    print(">> @Opt: Optimisation cycle complete after "+format(timer()-start, ".3f")+" sec.")
    
    # *****************************************************************************************************
    # * Evaluation Commands
    # *****************************************************************************************************
    
    c = evaluateResults("opt")
    d = evaluateResults("sim")
    
    # TODO extend MC logs
    COST.append(c)
    
np.savetxt("../log/Results_COSTDIST.csv", np.asarray(COST), delimiter=",")

print("Programme terminated!")