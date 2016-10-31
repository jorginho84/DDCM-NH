/*
This do-file estimates a wage process using the same sample of the auxiliary models

first:
do data_income.do
do sample_model.do

*/

clear
program drop _all
clear matrix
clear mata
set more off
set maxvar 15000

global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"


*These are the CPI factors (to 2003 dollars)
local cpi_0=178.3/148.4
local cpi_2=178.3/157.3
local cpi_5=178.3/168.3
local cpi_8=1




use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear


*Weekly wage (from annual figures)
*grossv2_y: gross earnings, including CSJs (W-2) payments from 
foreach x of numlist 0 1 4 7{
	replace grossv2_y`x'=grossv2_y`x'/52
}


*Hourly wages
foreach x of numlist 0 1 4 7{
	gen hwage_t`x'=grossv2_y`x'/hours_t`x'
}




/*
*They are already in 2003 dollars
*To real prices (2003 dollars)
replace hwage_t0=hwage_t0*`cpi_0'
replace hwage_t1=hwage_t1*`cpi_2'
replace hwage_t2=hwage_t2*`cpi_5'
replace hwage_t3=hwage_t3*`cpi_8'
*/

*log variables
gen lhwage_t0=log(hwage_t0)
gen lhwage_t1=log(hwage_t1)
gen lhwage_t4=log(hwage_t4)
gen lhwage_t7=log(hwage_t7)

*Age at each year
gen age_t1=age_ra+1
gen age_t4=age_ra+4
gen age_t7=age_ra+7


*Panel
egen id=group(sampleid child)
keep lhwage* age_t* d_HS2 id
reshape long lhwage_t age_t, i(id) j(t_ra)
xtset id t_ra

gen age_t2=age_t^2



**************************************************************************
**************************************************************************
**************************************************************************
/*

REGRESSION

*/
**************************************************************************
**************************************************************************
**************************************************************************


*xi: reg lhwage_t age_t age_t2 d_HS2
*matrix betas=_b[age_t]\_b[age_t2]\_b[d_HS2]\_b[_cons]\e(rmse)
*matrix sigma_aux=e(V)
*matrix sigma=sigma_aux[1,1]\sigma_aux[2,2]\sigma_aux[3,3]\

*Number of steps to bootstrap
local reps=1000

program reg_aux, rclass
	version 13
	args lhwage_t age_t age_t2 d_HS2
	xi: reg lhwage_t age_t age_t2 d_HS2
	return scalar beta_age=_b[age_t]
	return scalar beta_age2=_b[age_t2]
	return scalar beta_HS=_b[d_HS2]
	return scalar beta_cons=_b[_cons]
	return scalar sigma=e(rmse)^2
end
	


bootstrap beta_age=r(beta_age) beta_age2=r(beta_age2) beta_HS=r(beta_HS)/*
*/ beta_cons=r(beta_cons) sigma=r(sigma), /*
*/ reps(`reps'): reg_aux lhwage_t age_t age_t2 d_HS2
matrix beta_aux=e(b)
matrix betas=beta_aux'
matrix sigma_aux=e(V)
matrix sigma=sigma_aux[1,1]\sigma_aux[2,2]\sigma_aux[3,3]\sigma_aux[4,4]\sigma_aux[5,5]

*The order: age, age2, HS, const, and sigma


svmat betas
svmat sigma

preserve
keep betas*
drop if betas1==.
outsheet using "$results/wage_process/betas_v2.csv", comma  replace
restore

preserve
keep sigma*
drop if sigma1==.
outsheet using "$results/wage_process/sigma_v2.csv", comma  replace
restore


