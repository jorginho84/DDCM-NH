/*
This do-file simulates EITC for 0 and 1 children and makes a graph
*/

clear
set obs 10000

gen year=1996
gen depx=0
*gen depchild=1
gen state=50
gen mstat=1
egen pwages=seq()
taxsim9,replace
gen subsidy=-fiitax
keep pwages subsidy depx

tempfile data1
save `data1', replace


*Is tax credit differs if we modify just depx?

clear
set obs 10000

gen year=1996
gen depx=1
*gen depchild=1
gen state=50
gen mstat=1
egen pwages=seq()
taxsim9,replace
gen subsidy=-fiitax
keep pwages subsidy depx

append using `data1'


twoway (scatter subsidy pwages if depx==0) (scatter subsidy pwages if depx==1)



