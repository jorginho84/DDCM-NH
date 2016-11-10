/*
This do-file estimates moments based on the SSRS measure.

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


*Number of steps to bootstrap
local reps=1000


*******************************************************
/*Auxuliary model*/
*******************************************************
use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_theta_v2.dta", clear



*Leisure: 148-hours
foreach x of numlist 1 4 7{
	gen l_t`x'=148-hours_t`x'
	gen ll_t`x'_aux=log(l_t`x')
	egen mean_ll_t`x'_aux=mean(ll_t`x'_aux)
	gen ll_t`x'=ll_t`x'_aux - mean_ll_t`x'_aux
	drop mean_ll_t`x'_aux ll_t`x'_aux
}

*Income

gen incomepc_t1=(total_income_y1-cc_pay_t1*12)/(1 + nkids_year2 + married_year2)
gen incomepc_t4=(total_income_y4-cc_pay_t4*12)/(1 + nkids_year5 + married_year5)
gen incomepc_t7=(total_income_y7)/(1 + nkids_year8 + married_year8)

replace incomepc_t1=1 if incomepc_t1<0
replace incomepc_t4=1 if incomepc_t4<0
replace incomepc_t7=1 if incomepc_t7<0

foreach x of numlist 1 4 7{
	
	gen lincomepc_t`x'_aux=log(incomepc_t`x')
	egen mean_lincomepc_t`x'_aux=mean(lincomepc_t`x'_aux)
	gen lincomepc_t`x'=lincomepc_t`x'_aux - mean_lincomepc_t`x'_aux
	drop lincomepc_t`x'_aux mean_lincomepc_t`x'_aux

}

*Age of child
gen age_t1=age_t0+1
gen age_t4=age_t0+4
gen age_t7=age_t0+7

********************************************************************
/*Identifying period 2 measurement system*/
********************************************************************


*Inconditional Probs: matrix of 
*(to identify kappas)
/*
program prob_inc_g, rclass
	version 13
	args zm
	qui: sum `zm'
	return scalar mean_est=r(mean)
end
*/

matrix prob_inc_t2=J(4,3,.)
matrix sigma_prob_inc_t2=J(4,3,.)
foreach m of numlist 1 2 3{
	local jj=1
	foreach j of numlist 2 3 4 5{
		gen d_prob=skills_m`m'_t2==`j'
		replace d_prob=. if  skills_m`m'_t2==.
		qui: bootstrap mean_est=r(mean), reps(10): sum d_prob if d_prob!=.
		mat beta_aux=e(b)
		mat prob_inc_t2[`jj',`m']=beta_aux[1,1]
		mat sigma_aux=e(V)
		mat sigma_prob_inc_t2[`jj',`m']=sigma_aux[1,1]
		drop d_prob
		local jj=`jj'+1

	}

}

*Conditional probs: Matrix 2 (two differences)  x1
*To identify lambdas
mat prob_diff=J(2,1,.)
mat sigma_prob_diff=J(2,1,.)
gen d_m1=skills_m1_t2==5
replace d_m1=. if skills_m1_t2==.
gen d_m2=skills_m2_t2==5 /*this is the normalizing measure (lambda=1)*/
replace d_m2=. if skills_m2_t2==.

program prob_diff, rclass
	version 13
	args z_m1 z_m2
	tempname mean_1 mean_2
	qui: sum `z_m1' if `z_m2'==5 
	scalar `mean_1'=r(mean)
	qui: sum `z_m1' if `z_m2'==4
	scalar `mean_2'=r(mean)
	return scalar diff=`mean_1' - `mean_2'
end

bootstrap mean_diff=r(diff), reps(`reps'): prob_diff d_m1 skills_m2_t2 if (skills_m2_t2!=. & d_m1!=.)
mat beta_aux=e(b)
mat prob_diff[1,1]=beta_aux[1,1]
mat sigma_aux=e(V)
mat sigma_prob_diff[1,1]=sigma_aux[1,1]

bootstrap mean_diff=r(diff), reps(`reps'): prob_diff d_m2 skills_m3_t2 if (skills_m3_t2!=. & d_m2!=.)
mat beta_aux=e(b)
mat prob_diff[2,1]=beta_aux[1,1]
mat sigma_aux=e(V)
mat sigma_prob_diff[2,1]=sigma_aux[1,1]
drop d_m1 d_m2

********************************************************************
/*Identifying period 5 measurement system and prod function*/
********************************************************************

*To identify gammas (production function): 2 x 1 matrix
mat inputs_moments_old=J(2,1,.)
mat inputs_moments_young_cc0=J(2,1,.)
mat inputs_moments_young_cc1=J(2,1,.)

mat sigma_inputs_moments_old=J(2,1,.)
mat sigma_inputs_moments_young_cc0=J(2,1,.)
mat sigma_inputs_moments_young_cc1=J(2,1,.)

program input_diff, rclass
	version 13
	args loginput z_m
	tempname  mean_1 mean_2
	qui: sum `loginput' if `z_m'>=4
	scalar `mean_1'=r(mean)
	qui: sum `loginput' if `z_m'<=2
	scalar `mean_2'=r(mean)
	return scalar diff=`mean_1' - `mean_2'
end


	
*Old children: prod function
preserve
keep if age_t4>5
bootstrap mean_diff=r(diff), reps(`reps'): input_diff lincomepc_t4 skills_t5 if (lincomepc_t4!=. & skills_t5!=.)
mat beta_aux=e(b)
mat inputs_moments_old[1,1]=beta_aux[1,1]
mat sigma_aux=e(V)
mat sigma_inputs_moments_old[1,1]=sigma_aux[1,1]

bootstrap mean_diff=r(diff), reps(`reps'): input_diff ll_t4 skills_t5 if (ll_t4!=. & skills_t5!=.)
mat beta_aux=e(b)
mat inputs_moments_old[2,1]=beta_aux[1,1]
mat sigma_aux=e(V)
mat sigma_inputs_moments_old[2,1]=sigma_aux[1,1]
restore

*Young children/cc=0 and 1: produ function
forvalues cc=0/1{
	preserve
	keep if age_t4<=5 & d_CC2_t4==`cc'
	bootstrap mean_diff=r(diff), reps(`reps'): input_diff lincomepc_t4 skills_t5  if (lincomepc_t4!=. & skills_t5!=.)
	mat beta_aux=e(b)
	mat inputs_moments_young_cc`cc'[1,1]=beta_aux[1,1]
	mat sigma_aux=e(V)
	mat sigma_inputs_moments_young_cc`cc'[1,1]=sigma_aux[1,1]
	
	bootstrap mean_diff=r(diff), reps(`reps'): input_diff ll_t4 skills_t5  if (ll_t4!=. & skills_t5!=.)
	mat beta_aux=e(b)
	mat inputs_moments_young_cc`cc'[2,1]=beta_aux[1,1]
	mat sigma_aux=e(V)
	mat sigma_inputs_moments_young_cc`cc'[2,1]=sigma_aux[1,1]

	restore
}



*Inconditional Probs: matrix of 4 (categories) X 1 (measures)
*(to identify kappas)
matrix prob_inc_t5=J(4,1,.)
matrix sigma_prob_inc_t5=J(4,1,.)
local jj=1
foreach j of numlist 2 3 4 5{
	gen d_prob=skills_t5==`j'
	replace d_prob=. if  skills_t5==.
	qui: bootstrap mean_est=r(mean), reps(`reps'): sum d_prob if d_prob!=.
	mat beta_aux=e(b)
	mat prob_inc_t5[`jj',1]=beta_aux[1,1]
	mat sigma_aux=e(V)
	mat sigma_prob_inc_t5[`jj',1]=sigma_aux[1,1]
	drop d_prob
	local jj=`jj'+1

	}


*To identify lambda_t (t=5)
matrix prob_diff_t5=J(1,1,.)
matrix sigma_prob_diff_t5=J(1,1,.)
gen d_m1=skills_t5==5
replace d_m1=. if skills_t5==.

program prob_diff2, rclass
	version 13
	args z_m1 z_m2
	tempname mean_1 mean_2
	qui: sum `z_m1' if `z_m2'==5 
	scalar `mean_1'=r(mean)
	qui: sum `z_m1' if `z_m2'==4
	scalar `mean_2'=r(mean)
	return scalar diff=`mean_1' - `mean_2'
end


bootstrap mean_diff=r(diff), reps(`reps'): prob_diff d_m1 skills_m1_t2 if (d_m1!=. & skills_m1_t2!=.)
mat beta_aux=e(b)
mat prob_diff_t5[1,1]=beta_aux[1,1]
mat sigma_aux=e(V)
mat sigma_prob_diff_t5[1,1]=sigma_aux[1,1]
drop d_m1


**********************************************
**********************************************
**********************************************
/*Saving betas*/

*t=2
svmat prob_inc_t2 /*kappas: 4 (categories) X 3 (measures)*/
svmat prob_diff /*lambdas: 2 (two differences)  x1*/
svmat sigma_prob_inc_t2 
svmat sigma_prob_diff 


*t=5 and 2
svmat inputs_moments_old /*2 (leisure, income) x 1*/
svmat inputs_moments_young_cc0 /*2 (leisure, income) x 1*/
svmat inputs_moments_young_cc1 /*2 (leisure, income) x 1*/
svmat sigma_inputs_moments_old 
svmat sigma_inputs_moments_young_cc0 
svmat sigma_inputs_moments_young_cc1 

svmat prob_inc_t5 /*kappas: 4 (categories) X 1 (measures)*/
svmat prob_diff_t5 /*lambdas: 1 (difference)  x1*/
svmat sigma_prob_inc_t5 
svmat sigma_prob_diff_t5 

tempfile param
save `param', replace

*Saving betas
keep prob_inc_t2*
drop if  prob_inc_t21==.
outsheet using "$results/aux_model/prob_inc_t2.csv", comma  replace


foreach var in prob_diff inputs_moments_old /*
*/ inputs_moments_young_cc0 inputs_moments_young_cc1/*
*/ prob_inc_t5 prob_diff_t5{

	use `param', clear
	keep `var'1
	drop if `var'1==.
	outsheet using "$results/aux_model/`var'.csv", comma  replace

}


use `param', clear
keep sigma_prob_inc_t2*
drop if sigma_prob_inc_t21==.
outsheet using "$results/aux_model/sigma_prob_inc_t2.csv", comma  replace

*Saving sigmas
foreach var in   sigma_prob_diff  sigma_inputs_moments_old /*
*/  sigma_inputs_moments_young_cc0  sigma_inputs_moments_young_cc0  /*
*/ sigma_inputs_moments_young_cc1 sigma_prob_inc_t5  sigma_prob_diff_t5{

	use `param', clear
	keep `var'1
	drop if `var'1==.
	outsheet using "$results/aux_model/`var'.csv", comma  replace

}

