/*
This do-file computes ate on emp using bootstrap
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
	args d_year
	qui: sum `d_year' if d_RA==1
	scalar `mean_1'=r(mean)
	qui: sum `d_year' if d_RA==0
	scalar `mean_2'=r(mean)
	return scalar ate=`mean_1' - `mean_2'
end

mat ate_emp=J(9,1,.)
mat se_ate_emp=J(9,1,.)
foreach x in 0 1 4 7{
	gen d_emp_t`x' = hours_t`x'_cat1 == 0
	bootstrap diff=r(ate), reps(`reps'): prob_diff d_emp_t`x'
	mat ate_emp[`x'+1,1] = e(b)
	mat se_ate_emp[`x'+1,1] = e(se)

}

preserve
clear
set obs 9
svmat ate_emp
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_emp.csv", comma replace
restore

preserve
clear
set obs 9
svmat se_ate_emp
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_emp.csv", comma replace
restore


exit, STATA clear






