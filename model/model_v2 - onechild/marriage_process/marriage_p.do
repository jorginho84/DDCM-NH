/*
This do-file estimates a probit model for the probability of marriage given 
marital status in the previous period

The model:

P(m_t=1)=\Phi(X'\beta + *rho m_t-1)

It uses sample from th auxiliary model

*/


global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"

clear
clear matrix
clear mata
set more off
set maxvar 15000

use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model.dta", clear

rename married_year2 married_y2
rename married_year5 married_y5
drop married_year8


*Panel data
gen age_y0=age_ra
gen age_y2=age_ra+2
gen age_y5=age_ra+5

egen id=group(sampleid child)
keep married_y* id age_y* 

reshape long married_y age_y, i(id) j(t_ra)
gen t_prime=t_ra
replace t_prime=1 if t_ra==2
replace t_prime=2 if t_ra==5

*Working with first two periods
drop if t_prime==2

*Lagged variables
xtset id t_prime
gen married_y1=l.married_y
gen age_y1=l.age_y

*Regression: mt+1 on mt-1 (so I have to adjust coefficients)
xi: reg married_y age_y1 married_y1, robust

scalar define gamma_hat=(_b[married_y1] )^.5

scalar define beta2_hat=_b[age_y1]/(1+gamma_hat)

scalar define c_hat=(_b[_cons]-beta2_hat)/(1+gamma_hat)

scalar define sigma_hat= e(rmse)/(1+ gamma_hat^2)^.5

scalar list beta2_hat
scalar list gamma_hat
scalar list c_hat
scalar list sigma_hat


*Saving a database of coefficients
matrix betas=beta2_hat\gamma_hat\c_hat\sigma_hat


preserve

svmat betas
keep betas*
drop if betas1==.


outsheet using "$results/marriage_process/betas_m_v2.csv", comma  replace

restore

