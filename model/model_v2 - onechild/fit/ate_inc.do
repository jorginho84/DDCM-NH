/*This do-file compute ATE on income using bootstrap
*/


clear
program drop _all
clear matrix
clear mata
set more off


use "/home/jrodriguez/NH_HC/results/Model/sample_model.dta", clear
set seed 2828
local reps = 800

program inc_diff, rclass
	version 15
	tempname mean_1 mean_2
	args inc_year
	qui: sum `inc_year' if d_RA==1 & (agech_t2A<=6 | agech_t2B<=6)
	scalar `mean_1'=r(mean)
	qui: sum `inc_year' if d_RA==0 & (agech_t2A<=6 | agech_t2B<=6)
	scalar `mean_2'=r(mean)
	return scalar ate=`mean_1' - `mean_2'
end

*Only 3 years
mat ate_inc=J(3,1,.)
mat se_ate_inc=J(3,1,.)

*Income pc
gen incomepc_t1_aux=(total_income_y1-(cc_pay_t1A + cc_pay_t1B)*12)/(1 + nkids_year2 + married_year2)
gen incomepc_t4_aux=(total_income_y4-(cc_pay_t4A + cc_pay_t4B)*12)/(1 + nkids_year5 + married_year5)
gen incomepc_t7_aux=(total_income_y7)/(1 + nkids_year8 + married_year8)

replace incomepc_t1_aux=1 if incomepc_t1<0
replace incomepc_t4_aux=1 if incomepc_t4<0
replace incomepc_t7_aux=1 if incomepc_t7<0

gen incomepc_t1=log(incomepc_t1_aux)
gen incomepc_t4=log(incomepc_t4_aux)
gen incomepc_t7=log(incomepc_t7_aux)


*Child age at t=2
gen agech_t2A = age_t0A + 2
gen agech_t2B = age_t0B + 2

*Computing ATES for each year
local i =1
foreach x in 1 4 7{
	bootstrap diff=r(ate), reps(`reps'): inc_diff incomepc_t`x'_aux
	mat ate_inc[`i',1] = e(b)
	mat se_ate_inc[`i',1] = e(se)
	local i = `i' + 1

}


*Computing ATEs one period
mat ate_inc_2=J(1,1,.)
mat se_ate_inc_2=J(1,1,.)
bootstrap diff=r(ate), reps(`reps'): inc_diff incomepc_t1
mat ate_inc_2[1,1]=e(b)
mat se_ate_inc_2[1,1]=e(se)



*For each year
preserve
clear
set obs 3
svmat ate_inc
outsheet using "/home/jrodriguez/NH_HC/results/Model/fit/ate_inc.csv", comma replace
restore

preserve
clear
set obs 3
svmat se_ate_inc
outsheet using "/home/jrodriguez/NH_HC/results/Model/fit/se_ate_inc.csv", comma replace
restore

*Before
preserve
clear
set obs 1
svmat ate_inc_2
outsheet using "/home/jrodriguez/NH_HC/results/Model/fit/ate_inc_2.csv", comma replace
restore

preserve
clear
set obs 1
svmat se_ate_inc_2
outsheet using "/home/jrodriguez/NH_HC/results/Model/fit/se_ate_inc_2.csv", comma replace
restore


exit, STATA clear





