/*
This do-file computes the mean and variance of cc costs (for control group, conditional on paying)
*/


global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/aux_model"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model"

/*
robust SE for small samples. Set to hc3 for more conservatives. 

See Angrist and Pischke for more information
"robust" SE can be misleading when the sample size is small and there is no much heteroskedasticity.
*/
local SE="hc2"

clear
clear matrix
clear mata
set more off
set maxvar 15000


****************************************
/*Child care payments at t=1*/
****************************************
use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear

*Share of individuals with free child care
sum d_free if p_assign=="C" &  cc_pay_t1!=. & age_t0<=6 & d_CC2_t1==1
mat q_prob=r(mean)

*Distribution of prices for formal care users
keep if cc_pay_t1>0 & p_assign=="C" & cc_pay_t1!=. & age_t0<=6 & d_CC2_t1==1
rename cc_pay_t1 x
replace x=x*12
mlexp ( ln( exp({k}) ) + (exp({k})-1)*ln(x) - exp({k})*ln(exp({lambda})) - (x/exp({lambda}))^(exp({k})) )
mat betas=e(b)
scalar kapa=exp(betas[1,1])
scalar lambda=exp(betas[1,2])

gen cc_pay_sim=rweibull(kapa,lambda)

twoway (kdensity x) (kdensity cc_pay_sim)
graph export "$results/cccost_density.pdf", as(pdf) replace


matrix kapa=kapa
matrix lambda=lambda

svmat q_prob
svmat kapa
svmat lambda

preserve
keep q_prob1
drop if q_prob1==.
outsheet using "$results/q_prob.csv", comma  replace
restore

preserve
keep kapa1
drop if kapa1==.
outsheet using "$results/shape.csv", comma  replace
restore

preserve
keep lambda1
drop if lambda1==.
outsheet using "$results/scale.csv", comma  replace
restore
