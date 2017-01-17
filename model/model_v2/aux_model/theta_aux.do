/*
This do-file estimates moments based on the SSRS measure.

*/


 
*******************************************************
/*Auxuliary model*/
*******************************************************
use "$results/data_aux.dta", clear



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

replace incomepc_t1=0 if incomepc_t1<0
replace incomepc_t4=0 if incomepc_t4<0
replace incomepc_t7=0 if incomepc_t7<0

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



matrix prob_inc_t2=J(4*3,1,.)
local obs=1
foreach m of numlist 1 2 3{
	foreach j of numlist 2 3 4 5{
		gen d_prob=skills_m`m'_t2==`j'
		replace d_prob=. if  skills_m`m'_t2==.
		qui: sum d_prob if d_prob!=.
		mat beta_aux=r(mean)
		mat prob_inc_t2[`obs',1]=beta_aux[1,1]
		drop d_prob
		local obs=`obs'+1

	}

}



*Conditional probs: Matrix 2 (two differences)  x1
*To identify lambdas
mat prob_diff=J(2,1,.)

*Corr(m1,m2)
corr skills_m1_t2 skills_m2_t2
mat prob_diff[1,1] = r(rho)
*Corr(m1,m3)
corr skills_m1_t2 skills_m3_t2
mat prob_diff[2,1] = r(rho)



********************************************************************
/*Identifying period 5 measurement system and prod function*/
********************************************************************

*To identify gammas (production function): 2 x 1 matrix
mat inputs_moments_old=J(3,1,.)
mat inputs_moments_young_cc0=J(3,1,.)
mat inputs_moments_young_cc1=J(3,1,.)

mat sigma_inputs_moments_old=J(3,1,.)
mat sigma_inputs_moments_young_cc0=J(3,1,.)
mat sigma_inputs_moments_young_cc1=J(3,1,.)

program input_diff, rclass
	version 13
	args loginput z_m
	tempname  mean_1 mean_2
	qui: sum `loginput' if `z_m'>=3
	scalar `mean_1'=r(mean)
	qui: sum `loginput' if `z_m'<3
	scalar `mean_2'=r(mean)
	return scalar diff=`mean_1' - `mean_2'
end

program input_theta, rclass
	version 13
	args z_t2 z_t5
	tempname dummy_t5 dummy_t2 mean_1
	gen `dummy_t2'=`z_t2'>=3
	gen `dummy_t5'=`z_t5'>=3
	qui: sum `dummy_t5' if `dummy_t2'==1
	scalar `mean_1'=r(mean)
	return scalar mean_out=`mean_1'
end
	
*Old children: prod function
preserve
keep if age_t4>5
input_diff lincomepc_t4 skills_t5 if (lincomepc_t4!=. & skills_t5!=.)
mat inputs_moments_old[1,1]=r(diff)

input_diff ll_t4 skills_t5 if (ll_t4!=. & skills_t5!=.)
mat inputs_moments_old[2,1]=r(diff)

input_theta skills_m1_t2 skills_t5 if (skills_m1_t2!=. & skills_t5!=.)
mat inputs_moments_old[3,1]=r(mean_out)

restore



*Young children/cc=0 and 1: produ function
forvalues cc=0/1{

	preserve
	keep if age_t1<=5 & d_CC2_t1==`cc'
	input_diff lincomepc_t1 skills_m1_t2  if (lincomepc_t1!=. & skills_m1_t2!=.)
	mat inputs_moments_young_cc`cc'[1,1]=r(diff)
	
	input_diff ll_t1 skills_m1_t2  if (ll_t1!=. & skills_m1_t2!=.)
	mat inputs_moments_young_cc`cc'[2,1]=r(diff)
	
	input_theta skills_m1_t2 skills_t5 if (skills_m1_t2!=. & skills_t5!=.)
	mat inputs_moments_young_cc`cc'[3,1]=r(mean_out)
	
	restore
		
	
}

**********************************************************************************************
**********************************************************************************************
**********************************************************************************************

*Inconditional Probs: matrix of 4 (categories) X 1 (measures)
*(to identify kappas)
matrix prob_inc_t5=J(4,1,.)
local jj=1
foreach j of numlist 2 3 4 5{
	gen d_prob=skills_t5==`j'
	replace d_prob=. if  skills_t5==.
	sum d_prob if d_prob!=.
	mat prob_inc_t5[`jj',1]=r(mean)
	drop d_prob
	local jj=`jj'+1

	}


*To identify lambda_t (t=5)
matrix prob_diff_t5=J(1,1,.)

*corr(m1,m3)
corr skills_m1_t2 skills_t5
mat prob_diff_t5[1,1]=r(rho)



**********************************************
**********************************************
**********************************************
/*Saving betas*/

mat betas_prod = prob_inc_t2\prob_diff\prob_inc_t5\prob_diff_t5\inputs_moments_old\/*
*/inputs_moments_young_cc0\inputs_moments_young_cc1 


program drop input_diff input_theta 

