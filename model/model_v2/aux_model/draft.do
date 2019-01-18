/*
This do-file estimates a wage process using the same sample of the auxiliary models

first:
do data_income.do
do sample_model.do

*/





*These are the CPI factors (to 2003 dollars)
local cpi_0=178.3/148.4
local cpi_2=178.3/157.3
local cpi_5=178.3/168.3
local cpi_8=1




use "$results/sample_model.dta", clear

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

*Spouse income in real terms
replace income_spouse_y2 = income_spouse_y2*`cpi_5'

gen lincome_spouse_y2 = log(income_spouse_y2)

qui: reg lincome_spouse_y2 d_HS2

matrix beta_spouse = _b[d_HS2]\_b[_cons]\e(rmse)^2

matrix list beta_spouse


*log variables
gen lhwage_t0=log(hwage_t0)
gen lhwage_t1=log(hwage_t1)
gen lhwage_t4=log(hwage_t4)
gen lhwage_t7=log(hwage_t7)

*Age at each year
gen age_t1=age_ra+1
gen age_t4=age_ra+4
gen age_t7=age_ra+7

gen d_work_all = lhwage_t0!=.  & lhwage_t1!=. & lhwage_t4!=.  & lhwage_t7!=. 

*Panel
egen id=seq()
keep lhwage* age_ra d_HS2 id d_work_all higrade d_black p_assign
reshape long lhwage_t, i(id) j(t_ra)
xtset id t_ra

gen lt = log(t_ra + 1)

**************************************************************************
**************************************************************************
**************************************************************************
/*

REGRESSION

*/
**************************************************************************
**************************************************************************
**************************************************************************
xi: reg lhwage_t d_HS2 t_ra if d_work_all==1 & p_assign == "C"
matrix beta_aux=e(b)

predict u_hat , resid
gen u_hat_t1 = l.u_hat

reg u_hat l.u_hat if d_work_all==1, noc

matrix beta_wage=beta_aux'\e(rmse)^2\_b[L1.u_hat]
