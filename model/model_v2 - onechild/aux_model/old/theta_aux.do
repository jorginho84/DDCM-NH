/*
This do-file estimates 
*/


global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/aux_model"
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
set more off
program drop _all
set maxvar 15000



*******************************************************
/*Auxuliary model*/
*******************************************************
use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_theta_v2.dta", clear

*Standardize measures
foreach x of numlist 2 5 8{
rename skills_t`x' skills_t`x'_aux
egen skills_t`x'=std(skills_t`x'_aux)
local y=`x'-1
rename skills_t`x' skills_t`y' /*for compatibility w/ panel*/
rename skills_t`x'_aux skills_aux_t`y'
}



*Leisure: 148-hours
foreach x of numlist 1 4 7{
	gen l_t`x'=148-hours_t`x'
}

*Income

gen incomepc_t1=(total_income_y1-cc_pay_t1*12)/(1 + nkids_year2 + married_year2)
gen incomepc_t4=(total_income_y4-cc_pay_t4*12)/(1 + nkids_year5 + married_year5)
gen incomepc_t7=(total_income_y7)/(1 + nkids_year8 + married_year8)

replace incomepc_t1=1 if incomepc_t1<0
replace incomepc_t4=1 if incomepc_t4<0
replace incomepc_t7=1 if incomepc_t7<0

*Age of child
gen age_t1=age_t0+1
gen age_t4=age_t0+4
gen age_t7=age_t0+7

*Panel
egen childid=group(sampleid child)
keep childid age_t1 age_t4 age_t7 incomepc_t*  l_t* skills_t* skills_aux_t* d_CC*
reshape long age_t incomepc_t l_t skills_t skills_aux_t d_CC_t, i(childid) j(period)

*Set panel
replace period=2 if period==4
replace period=3 if period==7
xtset childid period


*Obtaining cutoffs
oprobit skills_aux_t
mat kappas_aux=e(b)
mat kappas=kappas_aux[1,1]\kappas_aux[1,2]\kappas_aux[1,3]\kappas_aux[1,4]


*Number of reps for bootstrap
local reps=1000


program theta_aux_1, rclass
	version 13
	args ranking x
	tempname mean_1 mean_2
	sum `x' if `ranking'==1 
	scalar `mean_1'=r(mean)
	sum `x' if `ranking'==5 
	scalar `mean_2'=r(mean)
	return scalar diff=`mean_2' - `mean_1'
end


program theta_aux_2, rclass
	version 13
	args ranking ranking_t1
	tempvar d_change
	gen `d_change'=`ranking'==`ranking_t1'
	sum `d_change'
	return scalar prob_tay=r(mean)
end

*Before running the program: drop all missing obs


*For all children
foreach x of varlist incomepc_t l_t{
	preserve
	drop if skills_aux_t==. | `x'==.
	bootstrap diff=r(diff), reps(`reps'): theta_aux_1 skills_aux_t `x'
	mat define beta_`x'=e(b)
	mat define sigma_`x'=e(se)
	restore
}

*For young children
foreach x of varlist d_CC_t{
	preserve
	keep if age_t<=5
	drop if skills_aux_t==. | `x'==.
	bootstrap diff=r(diff), reps(`reps'): theta_aux_1 skills_aux_t `x'
	mat define beta_`x'=e(b)
	mat define sigma_`x'=e(se)
	restore
}


preserve
keep if age>5
gen skills_aux_t1=l.skills_aux_t
drop if skills_aux_t==. | skills_aux_t1==.
bootstrap prob_tay=r(prob_tay), reps(`reps'): theta_aux_2 skills_aux_t skills_aux_t1
mat define beta_skills=e(b)
mat define sigma_skills=e(se)
restore



*Saving matrices
mat define betas_aux=beta_incomepc_t\beta_l_t\beta_d_CC_t
mat define sigma_aux=sigma_incomepc_t\sigma_l_t\sigma_d_CC_t

svmat kappas
svmat betas_aux
svmat sigma_aux
svmat beta_skills
svmat sigma_skills


foreach x in kappas betas_aux sigma_aux beta_skills sigma_skills{
	preserve
	keep `x'*
	drop if `x'1==.
	outsheet using "$results/aux_model/`x'_prodfunc.csv", comma  replace
	restore
}

stop!!!


************************************************************************
************************************************************************
/*   

Non-matched moments
Have to modify these: must account for discreteness of measure

*/

************************************************************************
************************************************************************
	
xi: reg skills_t1 i.p_assign
mat ate_theta=_b[_Ip_assign_2]

xi: reg skills_t2 i.p_assign
mat ate_theta=ate_theta\_b[_Ip_assign_2]

xi: reg skills_t3 i.p_assign
mat ate_theta=ate_theta\_b[_Ip_assign_2]

svmat ate_theta
preserve
keep ate_theta1
drop if ate_theta1==.	
outsheet using "$results/aux_model/ate_theta.csv", comma  replace
restore
