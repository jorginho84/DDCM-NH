/*
This do-file estimates the kids process.
It uses the sample of auxiliary models
Important: to identify the parameters of the kids process, must estimate marriage process first

The structual regression to identify

dkt+1=c + gamma1 age_t + gamma2 age_t^2 + phi1 k_t + beta2 m_t

k_t: number of kids at t
dk_t: if had a kid at t (kt-kt-1)
m_t: marriage dummy

*/


global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"

clear
clear matrix
scalar drop _all
clear mata
set more off
set maxvar 15000

*Recovering structurar parameters of marriage process
insheet using "$results/marriage_process/betas_m_v2.csv", comma names
mkmat betas1
scalar define c_tilde=betas1[3,1]
scalar define gamma1_tilde=betas1[2,1]
scalar define beta2_tilde=betas1[1,1]
scalar define sigma_m=betas1[4,1]

*Estimating kids process
use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model.dta", clear
rename married_year2 married_y2
rename married_year5 married_y5
drop married_year8

rename nkids_baseline nkids_y0
rename nkids_year2 nkids_y2
rename nkids_year5 nkids_y5
drop nkids_year8

*If had additional kid
gen born_y2=nkids_y2-nkids_y0
gen born_y5=nkids_y5-nkids_y2

*Panel data
gen age_y0=age_ra
gen age_y2=age_ra+2
gen age_y5=age_ra+5


egen id=group(sampleid child)
keep married_y* nkids_y* born_y* id age_y* 

reshape long married_y age_y nkids_y, i(id) j(t_ra)
gen t_prime=t_ra
replace t_prime=1 if t_ra==2
replace t_prime=2 if t_ra==5

*Working with first two periods
drop if t_prime==2

*Lagged variables
xtset id t_prime
gen married_t1=l.married_y
gen nkids_t1=l.nkids_y
gen age_y_2=age_y^2
gen age_y_t1=l.age_y
gen age_y_2_t1=l.age_y_2

*Regression
xi: reg nkids_y age_y_t1 age_y_2_t1 nkids_t1 married_t1



*Identifying structural parameters

scalar define beta1_hat=_b[nkids_t1]^.5
scalar define gamma2_hat=_b[age_y_2_t1]/(1+beta1_hat)
scalar define beta2_hat=_b[married_t1]/(beta1_hat + beta2_tilde)
scalar define gamma1_hat=(_b[age_y_t1] - 2*gamma2_hat - beta2_hat*gamma1_tilde)/(1 + beta1_hat)
scalar define c_hat=(_b[_cons] - gamma1_hat - gamma2_hat - beta2_hat*c_tilde)/(1 + beta1_hat)
scalar define phi1_hat=beta1_hat-1
scalar define sigma_hat=((e(rmse)^2 - (beta2_hat^2)*sigma_m^2)/(1 + beta1_hat^2))^.5


matrix betas=gamma1_hat\gamma2_hat\phi1_hat\beta2_hat\c_hat\sigma_hat


preserve

svmat betas
keep betas*
drop if betas1==.

outsheet using "$results/kids_process/betas_kids_v2.csv", comma  replace
restore








