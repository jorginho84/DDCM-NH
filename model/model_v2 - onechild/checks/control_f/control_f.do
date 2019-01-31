/*
This do file regresses log wages for those who work + control function
from structural model

*/


clear
program drop _all
clear matrix
clear mata
set more off
set maxvar 15000
set matsize 2000


global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/checks"

use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/checks/pscores.dta", clear
replace index = index + 1
tempfile data_p
save `data_p', replace

use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear
egen index=seq()


merge 1:1 index using `data_p'


local cpi_0=178.3/148.4
local cpi_2=178.3/157.3
local cpi_5=178.3/168.3
local cpi_8=1


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

gen d_work_all = lhwage_t0!=.  & lhwage_t1!=. & lhwage_t4!=.  & lhwage_t7!=. 

*Panel
egen id=seq()
keep lhwage* age_t* d_HS2 id d_work_all pscore*
reshape long lhwage_t age_t pscore, i(id) j(t_ra)
xtset id t_ra

gen age_t2=age_t^2

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
gen pscore2=pscore^2
gen pscore3=pscore^3
gen pscore4=pscore^4


xi: reg lhwage_t age_t age_t2 d_HS2 lt pscore pscore2 pscore3 pscore4, noc
local beta_age = string(round((_b[age_t]),0.001),"%9.3f")
local beta_age2 = string(round((_b[age_t2]),0.001),"%9.3f")
local beta_hs = string(round((_b[d_HS2]),0.001),"%9.3f")
local beta_lt = string(round((_b[lt]),0.001),"%9.3f")

predictnl xb = age_t*_b[age_t] + age_t2*_b[age_t2] + d_HS2*_b[d_HS2] + lt*_b[lt] if e(sample)
gen e_resid = lhwage_t - xb
sum e_resid if pscore>.95
local beta_c = string(round((r(mean)),0.001),"%9.3f")


file open controlf using "$results/control_f.tex", write replace
file write controlf "\begin{tabular}{lcccc}" _n
file write controlf "\hline" _n
file write controlf "Variables & & Structural && Control function \bigstrut\\" _n
file write controlf "\cline{1-1}\cline{3-5}Age   &       & -0.022 & &`beta_age'  \\" _n
file write controlf "Age\$^2\$ &       & 0.000 &       & `beta_age2' \\" _n
file write controlf "High school &       & 0.227 &       & `beta_hs' \\" _n
file write controlf "\$\log(t)\$ &       & 0.384 &       & `beta_lt' \\" _n
file write controlf "Constant &       & 1.449 &       & `beta_c' \bigstrut[b]\\" _n
file write controlf "\hline" _n
file write controlf "\end{tabular}%" _n
file close controlf


exit, STATA clear



