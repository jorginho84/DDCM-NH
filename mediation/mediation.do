/*
This do-file computes the mediation table using the same sample
of the model

*/


global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"

/*
robust SE for small samples. Set to hc3 for more conservatives. 

See Angrist and Pischke for more information
"robust" SE can be misleading when the sample size is small and there is no much heteroskedasticity.
*/
local SE="hc2"


clear
clear matrix
clear mata
set maxvar 15000
set more off

use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_theta.dta", clear


*Standardize measures
forvalues x=1/3{
rename skills_t`x' skills_t`x'_aux
egen skills_t`x'=std(skills_t`x'_aux)

}

*Considering income per capita
gen incomepc_t0=(total_income_t0)/(1 + nkids_baseline + married_y0)
gen incomepc_t1=(total_income_t1)/(1 + nkids_year2 + married_year2)
gen incomepc_t2=(total_income_t2)/(1 + nkids_year5 + married_year5)

*Log of income
foreach x of numlist 0 1 2 {
	gen l_earn_t`x'=log(incomepc_t`x')
	
}


*******************************************************************************************************************
**********************************YEAR-2 REGRESSION****************************************************************
*******************************************************************************************************************

*ATE
qui xi: reg skills_t1 i.p_assign
scalar ate=_b[_Ip_assign_2]



*Regression: can't do fixed effects b/c there is no variation in random assignment within family.
xi: reg skills_t1 i.p_assign d_CC l_earn_t0 hours_t0 age_ra d_marital_2 d_HS2

*saving coeffs
scalar n_y2=e(N)
scalar b_tau=_b[_Ip_assign_2]
scalar alpha_d_CC=_b[d_CC]
scalar alpha_l_earn_t0=_b[l_earn_t0]
scalar alpha_hours_t0=_b[hours_t0]


*Contributions
foreach variable of varlist d_CC l_earn_t0 hours_t0{
	qui xi: reg `variable' i.p_assign
	scalar delta_`variable'=_b[_Ip_assign_2]
	
	scalar cont_`variable'=_b[_Ip_assign_2]*alpha_`variable'
}


*******************************************************************************************************************
**********************************YEAR-5 REGRESSION****************************************************************
*******************************************************************************************************************
qui xi: reg skills_t2 i.p_assign
scalar ate_y5=_b[_Ip_assign_2]

*Regression: can't do fixed effects b/c there is no variation in random assignment within family.
xi: reg skills_t2 skills_t1 i.p_assign l_earn_t1 hours_t1 /* Current inputs
*/ d_CC  l_earn_t0 hours_t0 /* Past inputs
*/ age_ra d_marital_2 d_HS2 /*X's*/


*saving coeff
scalar n_y5=e(N)
scalar b_tau_y5=_b[_Ip_assign_2]
scalar alpha_skills_t1=_b[skills_t1]
scalar alpha_l_earn_t1=_b[l_earn_t1]
scalar alpha_hours_t1=_b[hours_t1]
scalar alpha_d_CC_y5=_b[d_CC]
scalar alpha_l_earn_t0=_b[l_earn_t0]
scalar alpha_hours_t0=_b[hours_t0]

*Contributions
foreach variable of varlist skills_t1 l_earn_t1 hours_t1 l_earn_t0 hours_t0{
	qui xi: reg `variable' i.p_assign
	scalar delta_`variable'_y5=_b[_Ip_assign_2]
	scalar cont_`variable'_y5=_b[_Ip_assign_2]*alpha_`variable'
}
scalar cont_d_CC_y5=delta_d_CC*alpha_d_CC_y5


*******************************************************************************************************************
**********************************YEAR-8 REGRESSION****************************************************************
*******************************************************************************************************************
*ATE
qui xi: reg skills_t3 i.p_assign
scalar ate_y8=_b[_Ip_assign_2]


*Regression: can't do fixed effects b/c there is no variation in random assignment within family.
xi: reg skills_t3 skills_t2 i.p_assign l_earn_t2 hours_t2 /* Current inputs
*/ d_CC  l_earn_t1 hours_t1 l_earn_t0 hours_t0 /* Past inputs
*/ age_ra d_marital_2 d_HS2/*X's*/

*saving coeff
scalar n_y8=e(N)
scalar b_tau_y8=_b[_Ip_assign_2]
scalar alpha_skills_t2=_b[skills_t2]
scalar alpha_l_earn_t2=_b[l_earn_t2]
scalar alpha_hours_t2=_b[hours_t2]
scalar alpha_l_earn_t1=_b[l_earn_t1]
scalar alpha_hours_t1=_b[hours_t1]
scalar alpha_d_CC_y8=_b[d_CC]
scalar alpha_l_earn_t0=_b[l_earn_t0]
scalar alpha_hours_t0=_b[hours_t0]


*Contributions
foreach variable of varlist skills_t2  l_earn_t2 hours_t2 l_earn_t1 hours_t1 l_earn_t0 hours_t0{
	qui xi: reg `variable' i.p_assign
	scalar delta_`variable'_y8=_b[_Ip_assign_2]
	scalar cont_`variable'_y8=_b[_Ip_assign_2]*alpha_`variable'
}
scalar cont_d_CC_y8=delta_d_CC*alpha_d_CC_y8


*********The table**************************

*The matrix:
mat A_y2=(cont_d_CC\0\cont_l_earn_t0\0\cont_hours_t0\0\b_tau\0\1\0\ate\0\n_y2)

mat A_y5=(cont_d_CC_y5\0\cont_l_earn_t0_y5\0\cont_hours_t0_y5\0\b_tau_y5\0\cont_skills_t1_y5\0\ate_y5\0\n_y5)

mat A_y8=(cont_d_CC_y8\0\cont_l_earn_t0_y8\0\cont_hours_t0_y8\0\b_tau_y8\0\cont_skills_t2_y8\0\ate_y8\0\n_y8)


mat A=A_y2,A_y5,A_y8

*Saving in excel
putexcel C4=matrix(A) using "$results/Mediation/med_table", sheet("data") modify




