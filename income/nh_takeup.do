/*
This do-file analyzes the take-up of New Hope

to run it:
1. run data_income.do
2. run sample_model.do
*/



global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"


clear
clear matrix
clear mata
scalar drop _all
set more off
program drop _all
set maxvar 15000


use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear


*Family size
gen nfam = 1 + nkids_baseline + married_y0

*NH Eligibility (for a family of 4 or less: fade out limit is 30,000)
gen d_elig_year0=(hours_t0>=30 & gross_nominal_y0<=30000 & p_assign=="E" & nfam<=4) | (hours_t0>=30 & gross_nominal_y0<=30300 & p_assign=="E" & nfam>4)
gen nh_takeup = sup_y0>0

*average take-up
sum nh_takeup if d_elig_year0==1

