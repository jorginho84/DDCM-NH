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

*Only 3 years
mat ate_inc=J(3,1,.)
mat se_ate_inc=J(3,1,.)

*Income pc
gen incomepc_t1=(total_income_y1-cc_pay_t1*12)/(1 + nkids_year2 + married_year2)
gen incomepc_t4=(total_income_y4-cc_pay_t4*12)/(1 + nkids_year5 + married_year5)
gen incomepc_t7=(total_income_y7)/(1 + nkids_year8 + married_year8)

replace incomepc_t1=0 if incomepc_t1<0
replace incomepc_t4=0 if incomepc_t4<0
replace incomepc_t7=0 if incomepc_t7<0


*Computing ATES for each year
local i =1
foreach x in 1 4 7{
	bootstrap diff=r(ate), reps(`reps'): inc_diff incomepc_t`x'
	mat ate_inc[`i',1] = e(b)
	mat se_ate_inc[`i',1] = e(se)
	local i = `i' + 1

}


*Computing ATEs before/after
egen child_id=group(sampleid child)
mat ate_inc_2=J(2,1,.)
mat se_ate_inc_2=J(2,1,.)

*Before
preserve
keep incomepc_t1 d_RA child_id

bootstrap diff=r(ate), reps(`reps'): inc_diff incomepc_t1
mat ate_inc_2[1,1]=e(b)
mat se_ate_inc_2[1,1]=e(se)

restore

*After
preserve
keep incomepc_t4 incomepc_t7 d_RA child_id
reshape long incomepc_t, i(child_id) j(year)

gen newid=child_id
bootstrap diff=r(ate), reps(`reps') cluster(child_id) idcluster(newid):/*
*/ inc_diff incomepc_t
mat ate_inc_2[2,1]=e(b)
mat se_ate_inc_2[2,1]=e(se)

restore



*For each year
preserve
clear
set obs 3
svmat ate_inc
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_inc.csv", comma replace
restore

preserve
clear
set obs 3
svmat se_ate_inc
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_inc.csv", comma replace
restore

*Before after
preserve
clear
set obs 2
svmat ate_inc_2
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_inc_2.csv", comma replace
restore

preserve
clear
set obs 2
svmat se_ate_inc_2
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_inc_2.csv", comma replace
restore


exit, STATA clear





