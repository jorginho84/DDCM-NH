/*

This do file presents evidence about assets holdings

*/


global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"

/*
robust SE for small samples. Set to hc3 for more conservatives. 

See Angrist and Pischke for more information
"robust" SE can be misleading when the sample size is small and there is no much heteroskedasticity.
*/
global SE "hc2"


clear
clear matrix
clear mata
set more off
set maxvar 15000

*******************************************************
/*Estimates from the youth database: year-5 results*/
*******************************************************

use "$databases/CFS_original.dta", clear

*labels
qui: do "$codes/data_cfs.do"


*Never seem to have money
tab piq195d if p_assign=="C" & piq195d!=" "

*Money for food
tab piq193d if p_assign=="C" & piq193d!=" "

*have money in case of emergency
tab piq196b if p_assign=="C" 

*have checkings accounts
tab piq196c if p_assign=="C"

*have savings accounts
tab piq196d if p_assign=="C" & piq196d!=" "

*have credit card accounts
tab piq196f if p_assign=="C" & piq196f!=" "

*have bank loans
tab piq196g if p_assign=="C" & piq196g!=" "


