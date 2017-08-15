clear all
clc

mc_noev = csvread('../log/noev/Results_MonteCarloDistributions.csv',1);
mc_uc = csvread('../log/uc/Results_MonteCarloDistributions.csv',1);
mc_pg = csvread('../log/pg/Results_MonteCarloDistributions.csv',1);
mc_h_dist_asc = csvread('../log/h_dist_asc/Results_MonteCarloDistributions.csv',1);
mc_h_dist_desc = csvread('../log/h_dist_desc/Results_MonteCarloDistributions.csv',1);
%mc_h_arr = csvread('../log/h_arr/Results_MonteCarloDistributions.csv',1);
mc_h_av = csvread('../log/h_av/Results_MonteCarloDistributions.csv',1);
mc_h_soc = csvread('../log/h_soc/Results_MonteCarloDistributions.csv',1);
mc_lp_ncon = csvread('../log/lp_ncon/Results_MonteCarloDistributions.csv',1);
mc_lp_con = csvread('../log/lp_con/Results_MonteCarloDistributions.csv',1);
mc_dem_mit = csvread('../log/dem_mit05/Results_MonteCarloDistributions.csv',1);
mc_av06 = csvread('../log/av06/Results_MonteCarloDistributions.csv',1);
mc_av07 = csvread('../log/av07/Results_MonteCarloDistributions.csv',1);
mc_av08 = csvread('../log/av08/Results_MonteCarloDistributions.csv',1);
mc_av09 = csvread('../log/av09/Results_MonteCarloDistributions.csv',1);
mc_pr090 = csvread('../log/pr090/Results_MonteCarloDistributions.csv',1);
mc_pr095 = csvread('../log/pr095/Results_MonteCarloDistributions.csv',1);
mc_pr099 = csvread('../log/pr099/Results_MonteCarloDistributions.csv',1);
mc_soc06 = csvread('../log/soc06/Results_MonteCarloDistributions.csv',1);
mc_soc07 = csvread('../log/soc07/Results_MonteCarloDistributions.csv',1);
mc_soc08 = csvread('../log/soc08/Results_MonteCarloDistributions.csv',1);
mc_joint = csvread('../log/joint/Results_MonteCarloDistributions.csv',1);

mc_spread1 = csvread('../log/spread1/Results_MonteCarloDistributions.csv',1);
mc_spread3 = csvread('../log/spread3/Results_MonteCarloDistributions.csv',1);
mc_spread5 = csvread('../log/spread5/Results_MonteCarloDistributions.csv',1);
mc_uc_spread1 = csvread('../log/uc_spread1/Results_MonteCarloDistributions.csv',1);
mc_uc_spread3 = csvread('../log/uc_spread3/Results_MonteCarloDistributions.csv',1);
mc_uc_spread5 = csvread('../log/uc_spread5/Results_MonteCarloDistributions.csv',1);
mc_pg_spread1 = csvread('../log/pg_spread1/Results_MonteCarloDistributions.csv',1);
mc_pg_spread3 = csvread('../log/pg_spread3/Results_MonteCarloDistributions.csv',1);
mc_pg_spread5 = csvread('../log/pg_spread5/Results_MonteCarloDistributions.csv',1);

% --------------------------------------------------------------------------------------------------------------------------------------------------
% plot start
% figure;
% subplot(2,2,1)
% group 1 cost
% x00 = zeros(20,1);
% y00 = zeros(20,1);
% x01 = mc_uc(1:20,9)./mc_uc(1:20,9);
% y01 = mc_uc(1:20,9)./mc_pg(1:20,9);
% x02 = mc_pg(1:20,9)./mc_uc(1:20,9);
% y02 = mc_pg(1:20,9)./mc_pg(1:20,9);
% 
% n00 = cat(2,x00,y00);
% n01 = cat(2,x01,y01);
% n02 = cat(2,x02,y02);
% 
% h = {n00,n01,n02};
% 
% aboxplot(h,'colorgrad','blue_up')
% legend('No Electric Vehicles', 'Uncontrolled Charging', 'Price-Based Heuristic')
% title('Charging Costs')
% hold on
% refline(0,1)
% 
% subplot(2,2,2)
% group 2 fulfilment
% x00 = zeros(20,1)
% y00 = zeros(20,1)
% x01 = mc_uc(1:20,10);
% y01 = mc_uc(1:20,11);
% x02 = mc_pg(1:20,10);
% y02 = mc_pg(1:20,11);
% 
% n00 = cat(2,x00,y00);
% n01 = cat(2,x01,y01);
% n02 = cat(2,x02,y02);
% 
% h = {n00,n01,n02};
% 
% aboxplot(h,'colorgrad','orange_up')
% legend('No Electric Vehicles', 'Uncontrolled Charging', 'Price-Based Heuristic')
% title('EV Demand Satisfaction')
% 
% subplot(2,2,3)
% group 3 constraint violation severity
% x00 = mc_noev(1:20,12);
% y00 = mc_noev(1:20,14);
% x01 = mc_uc(1:20,12);
% y01 = mc_uc(1:20,14);
% x02 = mc_pg(1:20,12);
% y02 = mc_pg(1:20,14);
% 
% n00 = cat(2,x00,y00);
% n01 = cat(2,x01,y01);
% n02 = cat(2,x02,y02);
% 
% h = {n00,n01,n02};
% 
% aboxplot(h,'colorgrad','red_up')
% legend('No Electric Vehicles', 'Uncontrolled Charging', 'Price-Based Heuristic')
% title('Constraint Violation Severity')
% hold on
% refline(0,1)
% refline(0,0.94)
% 
% 
% subplot(2,2,4)
% group 4 constraint viol frequency
% x00 = mc_noev(1:20,13);
% y00 = mc_noev(1:20,15);
% x01 = mc_uc(1:20,13);
% y01 = mc_uc(1:20,15);
% x02 = mc_pg(1:20,13);
% y02 = mc_pg(1:20,15);
% 
% n00 = cat(2,x00,y00);
% n01 = cat(2,x01,y01);
% n02 = cat(2,x02,y02);
% 
% h = {n00,n01,n02};
% 
% aboxplot(h,'colorgrad','green_up');
% title('Constraint Violation Frequency')
% legend('No Electric Vehicles', 'Uncontrolled Charging', 'Price-Based Heuristic')
% 
% --------------------------------------------------------------------------------------------------------------------------------------------------
% plot sim
% figure;
% subplot(2,2,1)
% group 1 cost
% x00 = zeros(20,1)
% y00 = zeros(20,1)
% x01 = mc_uc(1:20,9)./mc_uc(1:20,9)
% y01 = mc_uc(1:20,9)./mc_pg(1:20,9)
% x02 = mc_pg(1:20,9)./mc_uc(1:20,9)
% y02 = mc_pg(1:20,9)./mc_pg(1:20,9)
% x1 = mc_h_av(1:20,9)./mc_uc(1:20,9);
% y1 = mc_h_av(1:20,9)./mc_pg(1:20,9);
% x2 = mc_h_soc(1:20,9)./mc_uc(1:20,9);
% y2 = mc_h_soc(1:20,9)./mc_pg(1:20,9);
% x3 = mc_h_dist_asc(1:20,9)./mc_uc(1:20,9);
% y3 = mc_h_dist_asc(1:20,9)./mc_pg(1:20,9);
% x4 = mc_h_dist_desc(1:20,9)./mc_uc(1:20,9);
% y4 = mc_h_dist_desc(1:20,9)./mc_pg(1:20,9);
% x5 = mc_lp_ncon(1:20,9)./mc_uc(1:20,9);
% y5 = mc_lp_ncon(1:20,9)./mc_pg(1:20,9);
% x6 = mc_lp_con(1:20,9)./mc_uc(1:20,9);
% y6 = mc_lp_con(1:20,9)./mc_pg(1:20,9);
% 
% n00 = cat(2,x00,y00)
% n01 = cat(2,x01,y01)
% n02 = cat(2,x02,y02)
% n1 = cat(2,x1,y1);
% n2 = cat(2,x2,y2);
% n3 = cat(2,x3,y3);
% n4 = cat(2,x4,y4);
% n5 = cat(2,x5,y5);
% n6 = cat(2,x6,y6);
% 
% h = {n1,n2,n3,n4,n5,n6};
% 
% aboxplot(h,'labels',['Comparison to Uncontrolled Charging';'Comparison to Price-based Heuristic'],'colorgrad','blue_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Charging Costs')
% hold on
% refline(0,1)
% 
% subplot(2,2,2)
% group 2 fulfilment
% x00 = mc_noev(1:20,10)
% y00 = mc_noev(1:20,11)
% x01 = mc_uc(1:20,10)
% y01 = mc_uc(1:20,11)
% x02 = mc_pg(1:20,10)
% y02 = mc_pg(1:20,11)
% x1 = mc_h_av(1:20,10);
% y1 = mc_h_av(1:20,11);
% x2 = mc_h_soc(1:20,10);
% y2 = mc_h_soc(1:20,11);
% x3 = mc_h_dist_asc(1:20,10);
% y3 = mc_h_dist_asc(1:20,11);
% x4 = mc_h_dist_desc(1:20,10);
% y4 = mc_h_dist_desc(1:20,11);
% x5 = mc_lp_ncon(1:20,10);
% y5 = mc_lp_ncon(1:20,11);
% x6 = mc_lp_con(1:20,10);
% y6 = mc_lp_con(1:20,11);
% 
% n00 = cat(2,x00,y00)
% n01 = cat(2,x01,y01)
% n02 = cat(2,x02,y02)
% n1 = cat(2,x1,y1);
% n2 = cat(2,x2,y2);
% n3 = cat(2,x3,y3);
% n4 = cat(2,x4,y4);
% n5 = cat(2,x5,y5);
% n6 = cat(2,x6,y6);
% 
% h = {n1,n2,n3,n4,n5,n6};
% 
% aboxplot(h,'labels',['Average Battery SOC';'Minimum Battery SOC'],'colorgrad','orange_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('EV Demand Satisfaction')
% 
% subplot(2,2,3)
% group 3 constraint violation severity
% x00 = mc_noev(1:20,12)
% y00 = mc_noev(1:20,14)
% x01 = mc_uc(1:20,12)
% y01 = mc_uc(1:20,14)
% x02 = mc_pg(1:20,12)
% y02 = mc_pg(1:20,14)
% x1 = mc_h_av(1:20,12);
% y1 = mc_h_av(1:20,14);
% x2 = mc_h_soc(1:20,12);
% y2 = mc_h_soc(1:20,14);
% x3 = mc_h_dist_asc(1:20,12);
% y3 = mc_h_dist_asc(1:20,14);
% x4 = mc_h_dist_desc(1:20,12);
% y4 = mc_h_dist_desc(1:20,14);
% x5 = mc_lp_ncon(1:20,12);
% y5 = mc_lp_ncon(1:20,14);
% x6 = mc_lp_con(1:20,12);
% y6 = mc_lp_con(1:20,14);
% 
% n00 = cat(2,x00,y00)
% n01 = cat(2,x01,y01)
% n02 = cat(2,x02,y02)
% n1 = cat(2,x1,y1);
% n2 = cat(2,x2,y2);
% n3 = cat(2,x3,y3);
% n4 = cat(2,x4,y4);
% n5 = cat(2,x5,y5);
% n6 = cat(2,x6,y6);
% 
% h = {n1,n2,n3,n4,n5,n6};
% 
% aboxplot(h,'labels',['Maximum Loadings ratio of rating';'Minimum Voltages pu'],'colorgrad','red_up')
% aboxplot(h,'colorgrad','red_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Constraint Violation Severity')
% hold on
% refline(0,1)
% refline(0,0.94)
% 
% subplot(2,2,4)
% group 4 constraint viol frequency
% x00 = mc_noev(1:20,13)
% y00 = mc_noev(1:20,15)
% x01 = mc_uc(1:20,13)
% y01 = mc_uc(1:20,15)
% x02 = mc_pg(1:20,13)
% y02 = mc_pg(1:20,15)
% x1 = mc_h_av(1:20,13)
% y1 = mc_h_av(1:20,15)
% x2 = mc_h_soc(1:20,13)
% y2 = mc_h_soc(1:20,15)
% x3 = mc_h_dist_asc(1:20,13)
% y3 = mc_h_dist_asc(1:20,15)
% x4 = mc_h_dist_desc(1:20,13)
% y4 = mc_h_dist_desc(1:20,15)
% x5 = mc_lp_ncon(1:20,13)
% y5 = mc_lp_ncon(1:20,15)
% x6 = mc_lp_con(1:20,13)
% y6 = mc_lp_con(1:20,15)
% 
% n00 = cat(2,x00,y00)
% n01 = cat(2,x01,y01)
% n02 = cat(2,x02,y02)
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% n5 = cat(2,x5,y5)
% n6 = cat(2,x6,y6)
% 
% h = {n1,n2,n3,n4,n5,n6}
% 
% aboxplot(h,'labels',['Overloading Frequency (ratio of cases)';'Voltage Violation Frequency [ratio of cases]'],'colorgrad','green_up')
% aboxplot(h,'colorgrad','green_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Constraint Violation Frequency')

% --------------------------------------------------------------------------------------------------------------------------------------------------
% plot dem mit

% figure;
% subplot(2,2,1)
% % group 1 cost
% x01 = mc_lp_con(1:20,9)./mc_uc(1:20,9);
% y01 = mc_lp_con(1:20,9)./mc_pg(1:20,9);
% x02 = mc_dem_mit(1:20,9)./mc_uc(1:20,9);
% y02 = mc_dem_mit(1:20,9)./mc_pg(1:20,9);
% 
% n01 = cat(2,x01,y01);
% n02 = cat(2,x02,y02);
% 
% h = {n01,n02};
% 
% aboxplot(h,'colorgrad','blue_up')
% legend('No Electric Vehicles', 'Uncontrolled Charging', 'Price-Based Heuristic')
% title('Charging Costs')
% hold on
% refline(0,1)
% 
% subplot(2,2,2)
% % group 2 fulfilment
% x01 = mc_lp_con(1:20,10);
% y01 = mc_lp_con(1:20,11);
% x02 = mc_dem_mit(1:20,10);
% y02 = mc_dem_mit(1:20,11);
% 
% n01 = cat(2,x01,y01);
% n02 = cat(2,x02,y02);
% 
% h = {n01,n02};
% 
% aboxplot(h,'colorgrad','orange_up')
% legend('No Electric Vehicles', 'Uncontrolled Charging', 'Price-Based Heuristic')
% title('EV Demand Satisfaction')
% 
% subplot(2,2,3)
% % group 3 constraint violation severity
% x01 = mc_lp_con(1:20,12);
% y01 = mc_lp_con(1:20,14);
% x02 = mc_dem_mit(1:20,12);
% y02 = mc_dem_mit(1:20,14);
% 
% n01 = cat(2,x01,y01);
% n02 = cat(2,x02,y02);
% 
% h = {n01,n02};
% 
% aboxplot(h,'colorgrad','red_up')
% legend('No Electric Vehicles', 'Uncontrolled Charging', 'Price-Based Heuristic')
% title('Constraint Violation Severity')
% hold on
% refline(0,1)
% refline(0,0.94)
% 
% 
% subplot(2,2,4)
% % group 4 constraint viol frequency
% x01 = mc_lp_con(1:20,13);
% y01 = mc_lp_con(1:20,15);
% x02 = mc_dem_mit(1:20,13);
% y02 = mc_dem_mit(1:20,15);
% 
% n01 = cat(2,x01,y01);
% n02 = cat(2,x02,y02);
% 
% h = {n01,n02};
% 
% aboxplot(h,'colorgrad','green_up');
% title('Constraint Violation Frequency')
% legend('No Electric Vehicles', 'Uncontrolled Charging', 'Price-Based Heuristic')

% ---------------------------------------------------------------------------------------------------------------------------------------

% figure;
% 
% subplot(2,2,1)
% x1 = mc_lp_con(1:20,9)./mc_uc(1:20,9)
% y1 = mc_lp_con(1:20,9)./mc_pg(1:20,9)
% x2 = mc_av06(1:20,9)./mc_uc(1:20,9)
% y2 = mc_av06(1:20,9)./mc_pg(1:20,9)
% x3 = mc_av07(1:20,9)./mc_uc(1:20,9)
% y3 = mc_av07(1:20,9)./mc_pg(1:20,9)
% x4 = mc_av08(1:20,9)./mc_uc(1:20,9)
% y4 = mc_av08(1:20,9)./mc_pg(1:20,9)
% %x5 = mc_av09(1:20,9)./mc_uc(1:20,9)
% %y5 = mc_av09(1:20,9)./mc_pg(1:20,9)
% 
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% %n5 = cat(2,x5,y5)
% 
% h = {n1,n2,n3,n4}%,n5}
% 
% aboxplot(h,'labels',['Comparison to Uncontrolled Charging';'Comparison to Price-based Heuristic'],'colorgrad','blue_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Charging Costs')
% hold on
% refline(0,1)
% 
% subplot(2,2,2)
% %group 2 fulfilment
% x1 = mc_lp_con(1:20,10)
% y1 = mc_lp_con(1:20,11)
% x2 = mc_av06(1:20,10)
% y2 = mc_av06(1:20,11)
% x3 = mc_av07(1:20,10)
% y3 = mc_av07(1:20,11)
% x4 = mc_av08(1:20,10)
% y4 = mc_av08(1:20,11)
%x5 = mc_av09(1:20,10)
%y5 = mc_av09(1:20,11)
% 
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% 
% h = {n1,n2,n3,n4}
% 
% aboxplot(h,'labels',['Average Battery SOC';'Minimum Battery SOC'],'colorgrad','orange_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('EV Demand Satisfaction')
% 
% subplot(2,2,3)
% %group 3 constraint violation severity
% x1 = mc_lp_con(1:20,12)
% y1 = mc_lp_con(1:20,14)
% x2 = mc_av06(1:20,12)
% y2 = mc_av06(1:20,14)
% x3 = mc_av07(1:20,12)
% y3 = mc_av07(1:20,14)
% x4 = mc_av08(1:20,12)
% y4 = mc_av08(1:20,14)
% %x5 = mc_av09(1:20,12)
% %y5 = mc_av09(1:20,14)
% 
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% %n5 = cat(2,x5,y5)
% 
% h = {n1,n2,n3,n4}%,n5}
% 
% aboxplot(h,'colorgrad','red_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Constraint Violation Severity')
% hold on
% refline(0,1)
% refline(0,0.94)
% 
% subplot(2,2,4)
% %group 4 constraint viol frequency
% x1 = mc_lp_con(1:20,13)
% y1 = mc_lp_con(1:20,15)
% x2 = mc_av06(1:20,13)
% y2 = mc_av06(1:20,15)
% x3 = mc_av07(1:20,13)
% y3 = mc_av07(1:20,15)
% x4 = mc_av08(1:20,13)
% y4 = mc_av08(1:20,15)
% %x5 = mc_av09(1:20,13)
% %y5 = mc_av09(1:20,15)
% 
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% %n5 = cat(2,x5,y5)
% 
% h = {n1,n2,n3,n4}%,n5}
% 
% aboxplot(h,'colorgrad','green_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Constraint Violation Frequency')

% ---------------------------------------------------------------------------------------------------------------------------------------

% figure;
% 
% subplot(2,2,1)
% x1 = mc_lp_con(1:20,9)./mc_uc(1:20,9)
% y1 = mc_lp_con(1:20,9)./mc_pg(1:20,9)
% x2 = mc_soc06(1:20,9)./mc_uc(1:20,9)
% y2 = mc_soc06(1:20,9)./mc_pg(1:20,9)
% x3 = mc_soc07(1:20,9)./mc_uc(1:20,9)
% y3 = mc_soc07(1:20,9)./mc_pg(1:20,9)
% x4 = mc_soc08(1:20,9)./mc_uc(1:20,9)
% y4 = mc_soc08(1:20,9)./mc_pg(1:20,9)
% %x5 = mc_av09(1:20,9)./mc_uc(1:20,9)
% %y5 = mc_av09(1:20,9)./mc_pg(1:20,9)
% 
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% %n5 = cat(2,x5,y5)
% 
% h = {n1,n2,n3,n4}%,n5}
% 
% aboxplot(h,'labels',['Comparison to Uncontrolled Charging';'Comparison to Price-based Heuristic'],'colorgrad','blue_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Charging Costs')
% hold on
% refline(0,1)
% 
% subplot(2,2,2)
% %group 2 fulfilment
% x1 = mc_lp_con(1:20,10)
% y1 = mc_lp_con(1:20,11)
% x2 = mc_soc06(1:20,10)
% y2 = mc_soc06(1:20,11)
% x3 = mc_soc07(1:20,10)
% y3 = mc_soc07(1:20,11)
% x4 = mc_soc08(1:20,10)
% y4 = mc_soc08(1:20,11)
% %x5 = mc_av09(1:20,10)
% %y5 = mc_av09(1:20,11)
% 
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% 
% h = {n1,n2,n3,n4}
% 
% aboxplot(h,'labels',['Average Battery SOC';'Minimum Battery SOC'],'colorgrad','orange_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('EV Demand Satisfaction')
% 
% subplot(2,2,3)
% %group 3 constraint violation severity
% x1 = mc_lp_con(1:20,12)
% y1 = mc_lp_con(1:20,14)
% x2 = mc_soc06(1:20,12)
% y2 = mc_soc06(1:20,14)
% x3 = mc_soc07(1:20,12)
% y3 = mc_soc07(1:20,14)
% x4 = mc_soc08(1:20,12)
% y4 = mc_soc08(1:20,14)
% %x5 = mc_av09(1:20,12)
% %y5 = mc_av09(1:20,14)
% 
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% %n5 = cat(2,x5,y5)
% 
% h = {n1,n2,n3,n4}%,n5}
% 
% aboxplot(h,'colorgrad','red_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Constraint Violation Severity')
% hold on
% refline(0,1)
% refline(0,0.94)
% 
% subplot(2,2,4)
% %group 4 constraint viol frequency
% x1 = mc_lp_con(1:20,13)
% y1 = mc_lp_con(1:20,15)
% x2 = mc_soc06(1:20,13)
% y2 = mc_soc06(1:20,15)
% x3 = mc_soc07(1:20,13)
% y3 = mc_soc07(1:20,15)
% x4 = mc_soc08(1:20,13)
% y4 = mc_soc08(1:20,15)
% %x5 = mc_av09(1:20,13)
% %y5 = mc_av09(1:20,15)
% 
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% %n5 = cat(2,x5,y5)
% 
% h = {n1,n2,n3,n4}%,n5}
% 
% aboxplot(h,'colorgrad','green_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Constraint Violation Frequency')

% ---------------------------------------------------------------------------------------------------------------------------------------

% figure;
% 
% subplot(2,2,1)
% x1 = mc_lp_con(1:20,9)./mc_uc(1:20,9)
% y1 = mc_lp_con(1:20,9)./mc_pg(1:20,9)
% x2 = mc_pr090(1:20,9)./mc_uc(1:20,9)
% y2 = mc_pr090(1:20,9)./mc_pg(1:20,9)
% x3 = mc_pr095(1:20,9)./mc_uc(1:20,9)
% y3 = mc_pr095(1:20,9)./mc_pg(1:20,9)
% x4 = mc_pr099(1:20,9)./mc_uc(1:20,9)
% y4 = mc_pr099(1:20,9)./mc_pg(1:20,9)
% %x5 = mc_av09(1:20,9)./mc_uc(1:20,9)
% %y5 = mc_av09(1:20,9)./mc_pg(1:20,9)
% 
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% %n5 = cat(2,x5,y5)
% 
% h = {n1,n2,n3,n4}%,n5}
% 
% aboxplot(h,'labels',['Comparison to Uncontrolled Charging';'Comparison to Price-based Heuristic'],'colorgrad','blue_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Charging Costs')
% hold on
% refline(0,1)
% 
% subplot(2,2,2)
% %group 2 fulfilment
% x1 = mc_lp_con(1:20,10)
% y1 = mc_lp_con(1:20,11)
% x2 = mc_pr090(1:20,10)
% y2 = mc_pr090(1:20,11)
% x3 = mc_pr095(1:20,10)
% y3 = mc_pr095(1:20,11)
% x4 = mc_pr099(1:20,10)
% y4 = mc_pr099(1:20,11)
% %x5 = mc_av09(1:20,10)
% %y5 = mc_av09(1:20,11)
% 
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% 
% h = {n1,n2,n3,n4}
% 
% aboxplot(h,'labels',['Average Battery SOC';'Minimum Battery SOC'],'colorgrad','orange_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('EV Demand Satisfaction')
% 
% subplot(2,2,3)
% %group 3 constraint violation severity
% x1 = mc_lp_con(1:20,12)
% y1 = mc_lp_con(1:20,14)
% x2 = mc_pr090(1:20,12)
% y2 = mc_pr090(1:20,14)
% x3 = mc_pr095(1:20,12)
% y3 = mc_pr095(1:20,14)
% x4 = mc_pr099(1:20,12)
% y4 = mc_pr099(1:20,14)
% %x5 = mc_av09(1:20,12)
% %y5 = mc_av09(1:20,14)
% 
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% %n5 = cat(2,x5,y5)
% 
% h = {n1,n2,n3,n4}%,n5}
% 
% aboxplot(h,'colorgrad','red_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Constraint Violation Severity')
% hold on
% refline(0,1)
% refline(0,0.94)
% 
% subplot(2,2,4)
% %group 4 constraint viol frequency
% x1 = mc_lp_con(1:20,13)
% y1 = mc_lp_con(1:20,15)
% x2 = mc_pr090(1:20,13)
% y2 = mc_pr090(1:20,15)
% x3 = mc_pr095(1:20,13)
% y3 = mc_pr095(1:20,15)
% x4 = mc_pr099(1:20,13)
% y4 = mc_pr099(1:20,15)
% %x5 = mc_av09(1:20,13)
% %y5 = mc_av09(1:20,15)
% 
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% %n5 = cat(2,x5,y5)
% 
% h = {n1,n2,n3,n4}%,n5}
% 
% aboxplot(h,'colorgrad','green_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Constraint Violation Frequency')

% ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
% ---------------------------------------------------------------------------------------------------------------------------------------
% 
% figure;
% 
% subplot(2,2,1)
% x1 = mc_h_soc(1:20,9)./mc_uc(1:20,9)
% y1 = mc_h_soc(1:20,9)./mc_pg(1:20,9)
% x2 = mc_lp_ncon(1:20,9)./mc_uc(1:20,9)
% y2 = mc_lp_ncon(1:20,9)./mc_pg(1:20,9)
% x3 = mc_lp_con(1:20,9)./mc_uc(1:20,9)
% y3 = mc_lp_con(1:20,9)./mc_pg(1:20,9)
% x4 = mc_joint(1:20,9)./mc_uc(1:20,9)
% y4 = mc_joint(1:20,9)./mc_pg(1:20,9)
% %x5 = mc_av09(1:20,9)./mc_uc(1:20,9)
% %y5 = mc_av09(1:20,9)./mc_pg(1:20,9)
% 
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% %n5 = cat(2,x5,y5)
% 
% h = {n1,n2,n3,n4}%,n5}
% 
% aboxplot(h,'labels',['Comparison to Uncontrolled Charging';'Comparison to Price-based Heuristic'],'colorgrad','blue_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Charging Costs')
% hold on
% refline(0,1)
% 
% subplot(2,2,2)
% %group 2 fulfilment
% x1 = mc_h_soc(1:20,10)
% y1 = mc_h_soc(1:20,11)
% x2 = mc_lp_ncon(1:20,10)
% y2 = mc_lp_ncon(1:20,11)
% x3 = mc_lp_con(1:20,10)
% y3 = mc_lp_con(1:20,11)
% x4 = mc_joint(1:20,10)
% y4 = mc_joint(1:20,11)
% %x5 = mc_av09(1:20,10)
% %y5 = mc_av09(1:20,11)
% 
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% 
% h = {n1,n2,n3,n4}
% 
% aboxplot(h,'labels',['Average Battery SOC';'Minimum Battery SOC'],'colorgrad','orange_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('EV Demand Satisfaction')
% 
% subplot(2,2,3)
% %group 3 constraint violation severity
% x1 = mc_h_soc(1:20,12)
% y1 = mc_h_soc(1:20,14)
% x2 = mc_lp_ncon(1:20,12)
% y2 = mc_lp_ncon(1:20,14)
% x3 = mc_lp_con(1:20,12)
% y3 = mc_lp_con(1:20,14)
% x4 = mc_joint(1:20,12)
% y4 = mc_joint(1:20,14)
% %x5 = mc_av09(1:20,12)
% %y5 = mc_av09(1:20,14)
% 
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% %n5 = cat(2,x5,y5)
% 
% h = {n1,n2,n3,n4}%,n5}
% 
% aboxplot(h,'colorgrad','red_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Constraint Violation Severity')
% hold on
% refline(0,1)
% refline(0,0.94)
% 
% subplot(2,2,4)
% %group 4 constraint viol frequency
% x1 = mc_h_soc(1:20,13)
% y1 = mc_h_soc(1:20,15)
% x2 = mc_lp_ncon(1:20,13)
% y2 = mc_lp_ncon(1:20,15)
% x3 = mc_lp_con(1:20,13)
% y3 = mc_lp_con(1:20,15)
% x4 = mc_joint(1:20,13)
% y4 = mc_joint(1:20,15)
% %x5 = mc_av09(1:20,13)
% %y5 = mc_av09(1:20,15)
% 
% n1 = cat(2,x1,y1)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
% %n5 = cat(2,x5,y5)
% 
% h = {n1,n2,n3,n4}%,n5}
% 
% aboxplot(h,'colorgrad','green_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Constraint Violation Frequency')

% --------------------------
% prices
% figure;
% subplot(1,2,1)
% x1 = mc_spread1(1:20,9)./mc_uc_spread1(1:20,9)
% y1 = mc_spread1(1:20,9)./mc_pg_spread1(1:20,9)
% x2 = mc_spread3(1:20,9)./mc_uc_spread3(1:20,9)
% y2 = mc_spread3(1:20,9)./mc_pg_spread3(1:20,9)
% x3 = mc_spread5(1:20,9)./mc_uc_spread5(1:20,9)
% y3 = mc_spread5(1:20,9)./mc_pg_spread5(1:20,9)
%x4 = mc_joint(1:20,9)./mc_uc(1:20,9)
%y4 = mc_joint(1:20,9)./mc_pg(1:20,9)
%x5 = mc_av09(1:20,9)./mc_uc(1:20,9)
%y5 = mc_av09(1:20,9)./mc_pg(1:20,9)

%n1 = cat(2,x1,y1)
%n2 = cat(2,x2,y2)
%n3 = cat(2,x3,y3)
%n4 = cat(2,x4,y4)
%n5 = cat(2,x5,y5)

% h = {x1,x2,x3}%,n4}%,n5}
% 
% aboxplot(h,'labels',['Comparison to Uncontrolled Charging';'Comparison to Price-based Heuristic'],'colorgrad','blue_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Charging Costs')
% hold on
% refline(0,1)
% 
% subplot(1,2,2)
% x1 = mc_spread1(1:20,9)./mc_uc_spread1(1:20,9)
% y1 = mc_spread1(1:20,9)./mc_pg_spread1(1:20,9)
% x2 = mc_spread3(1:20,9)./mc_uc_spread3(1:20,9)
% y2 = mc_spread3(1:20,9)./mc_pg_spread3(1:20,9)
% x3 = mc_spread5(1:20,9)./mc_uc_spread5(1:20,9)
% y3 = mc_spread5(1:20,9)./mc_pg_spread5(1:20,9)
% %x4 = mc_joint(1:20,9)./mc_uc(1:20,9)
% %y4 = mc_joint(1:20,9)./mc_pg(1:20,9)
% %x5 = mc_av09(1:20,9)./mc_uc(1:20,9)
% %y5 = mc_av09(1:20,9)./mc_pg(1:20,9)
% 
% %n1 = cat(2,x1,y1)
% %n2 = cat(2,x2,y2)
% %n3 = cat(2,x3,y3)
% %n4 = cat(2,x4,y4)
% %n5 = cat(2,x5,y5)
% 
% h = {y1,y2,y3}%,n4}%,n5}
% 
% aboxplot(h,'labels',['Comparison to Uncontrolled Charging';'Comparison to Price-based Heuristic'],'colorgrad','blue_up')
% legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
% title('Charging Costs')
% hold on
% refline(0,1)

figure;

x1 = mc_lp_con(1:20,9)./mc_lp_con(1:20,2)
x2 = mc_pr090(1:20,9)./mc_pr090(1:20,2)
x3 = mc_pr095(1:20,9)./mc_pr095(1:20,2)
x4 = mc_pr099(1:20,9)./mc_pr099(1:20,2)
%x5 = mc_av09(1:20,9)./mc_uc(1:20,9)
%y5 = mc_av09(1:20,9)./mc_pg(1:20,9)

n1 = cat(2,x1,x2,x3,x4)
% n2 = cat(2,x2,y2)
% n3 = cat(2,x3,y3)
% n4 = cat(2,x4,y4)
%n5 = cat(2,x5,y5)

h = {n1}%,n5}

aboxplot(h,'labels',['Comparison to Uncontrolled Charging';'Comparison to Price-based Heuristic'],'colorgrad','blue_up')
legend('heuristic (availability)', 'heuristic (SOC)', 'heuristic (distance asc.)', 'heuristic (distance desc.)', 'LP (with frequent cycles)','LP (without frequent cycles)')
title('Charging Costs')