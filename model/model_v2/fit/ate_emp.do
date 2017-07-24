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

*This program computes ATE for a given year
program prob_diff, rclass
	version 13
	tempname mean_1 mean_2
	args emp
	qui: sum `emp' if d_RA==1
	scalar `mean_1'=r(mean)
	qui: sum `emp' if d_RA==0
	scalar `mean_2'=r(mean)
	return scalar ate=`mean_1' - `mean_2'
end


*Computing ATEs for each year
mat ate_part=J(9,1,.)
mat se_ate_part=J(9,1,.)
mat ate_full=J(9,1,.)
mat se_ate_full=J(9,1,.)
mat ate_hours=J(9,1,.)
mat se_ate_hours=J(9,1,.)
foreach x in 0 1 4 7{
	gen d_part_t`x' = hours_t`x'_cat2 == 1
	gen d_full_t`x' = hours_t`x'_cat3 == 1

	
	bootstrap diff=r(ate), reps(`reps'): prob_diff d_part_t`x'
	mat ate_part[`x'+1,1] = e(b)
	mat se_ate_part[`x'+1,1] = e(se)

	bootstrap diff=r(ate), reps(`reps'): prob_diff d_full_t`x'
	mat ate_full[`x'+1,1] = e(b)
	mat se_ate_full[`x'+1,1] = e(se)

	bootstrap diff=r(ate), reps(`reps'): prob_diff hours_t`x'
	mat ate_hours[`x'+1,1] = e(b)
	mat se_ate_hours[`x'+1,1] = e(se)

}

*Computing ATEs before/after
egen child_id=group(sampleid child)

mat ate_part_2=J(2,1,.)
mat se_ate_part_2=J(2,1,.)
mat ate_full_2=J(2,1,.)
mat se_ate_full_2=J(2,1,.)
mat ate_hours_2=J(1,1,.)
mat se_ate_hours_2=J(1,1,.)

*Before
preserve

keep d_part_t0 d_part_t1 d_full_t0 d_full_t1 hours_t0 hours_t1 d_RA child_id
reshape long d_full_t d_part_t hours_t, i(child_id) j(year)

gen newid = child_id

foreach var in part full{
	bootstrap diff=r(ate), reps(`reps') cluster(child_id) idcluster(newid): prob_diff d_`var'_t
	mat ate_`var'_2[1,1]  =e(b)
	mat se_ate_`var'_2[1,1]  =e(se)
}

bootstrap diff=r(ate), reps(`reps') cluster(child_id) idcluster(newid): prob_diff hours_t
mat ate_hours_2[1,1]  =e(b)
mat se_ate_hours_2[1,1]  =e(se)

restore



foreach vars in part full hours{

	*For each year
	preserve
	clear
	set obs 9
	svmat ate_`vars'
	outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_`vars'.csv", comma replace
	restore

	preserve
	clear
	set obs 9
	svmat se_ate_`vars'
	outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_`vars'.csv", comma replace
	restore

	*Before/after
	preserve
	clear
	set obs 1
	svmat ate_`vars'_2
	outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_`vars'_2.csv", comma replace
	restore

	preserve
	clear
	set obs 1
	svmat se_ate_`vars'_2
	outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_`vars'_2.csv", comma replace
	restore

} 


exit, STATA clear






