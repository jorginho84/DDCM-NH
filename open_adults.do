

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

use "$databases/Adults_original.dta", clear

*labels
*do "$codes/data_cfs.do"
