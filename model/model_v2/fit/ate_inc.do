/*This do-file compute ATE on income using bootstrap
*/


clear
program drop _all
clear matrix
clear mata
set more off


use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear
set seed 2828
local reps = 800

program inc_diff, rclass
	version 13
	tempname mean_1 mean_2
	args inc_year
	qui: sum `inc_year' if d_RA==1
	scalar `mean_1'=r(mean)
	qui: sum `inc_year' if d_RA==0
	scalar `mean_2'=r(mean)
	return scalar ate=`mean_1' - `mean_2'
end

mat ate_inc=J(9,1,.)
mat se_ate_inc=J(9,1,.)

forvalues x=0/8{
	bootstrap diff=r(ate), reps(`reps'): inc_diff total_income_y`x'
	mat ate_inc[`x'+1,1] = e(b)
	mat se_ate_inc[`x'+1,1] = e(se)

}


preserve
clear
set obs 9
svmat ate_inc
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_inc.csv", comma replace
restore

preserve
clear
set obs 9
svmat se_ate_inc
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_inc.csv", comma replace
restore


exit, STATA clear





