/*
This do-file computes ATE on child care decisions
*/


clear
program drop _all
clear matrix
clear mata
set more off


use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear
set seed 2828
local reps = 800

program prob_diff, rclass
	version 13
	tempname mean_1 mean_2
	args cc_t
	qui: sum `cc_t' if d_RA==1
	scalar `mean_1'=r(mean)
	qui: sum `cc_t' if d_RA==0
	scalar `mean_2'=r(mean)
	return scalar ate=`mean_1' - `mean_2'
end

*Identifying young children
gen age_t1=age_t0+1
gen age_t2=age_t0+2
gen age_t4=age_t0+4
gen age_t7=age_t0+7


*Computing ATE for each year
mat ate_cc=J(2,1,.)
mat se_ate_cc=J(2,1,.)

local i =1
foreach x in 1 4 {/*No young children in t=7*/
	bootstrap diff=r(ate), reps(`reps'): prob_diff d_CC2_t`x' if age_t2<=6
	mat ate_cc[`i',1]=e(b)
	mat se_ate_cc[`i',1]=e(se)
	local i = `i' + 1

}

preserve
clear
set obs 2
svmat ate_cc
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_cc.csv", comma replace
restore

preserve
clear
set obs 2
svmat se_ate_cc
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_cc.csv", comma replace
restore

exit, STATA clear



