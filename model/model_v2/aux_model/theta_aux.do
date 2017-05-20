/*
This do-file estimates moments based on the SSRS measure.

*/


 
*******************************************************
/*Auxuliary model*/
*******************************************************
use "$results/data_aux.dta", clear

*Standardized measures
foreach x of numlist 2 5 8{
rename skills_t`x' skills_t`x'_aux
egen skills_t`x'=std(skills_t`x'_aux)

}


*Leisure: 148-hours
foreach x of numlist 1 4 7{
	gen l_t`x'=148-hours_t`x'
}

*Income

gen incomepc_t1=(total_income_y1-cc_pay_t1*12)/(1 + nkids_year2 + married_year2)
gen incomepc_t4=(total_income_y4-cc_pay_t4*12)/(1 + nkids_year5 + married_year5)
gen incomepc_t7=(total_income_y7)/(1 + nkids_year8 + married_year8)

replace incomepc_t1=1 if incomepc_t1<=0
replace incomepc_t4=1 if incomepc_t4<=0
replace incomepc_t7=1 if incomepc_t7<=0

*Age of child
gen age_t1=age_t0+1
gen age_t4=age_t0+4
gen age_t7=age_t0+7

********************************************************************
/*Identifying period 2 measurement system*/
********************************************************************



matrix prob_inc_t2=J(4,1,.)
local obs=1
foreach j of numlist 2 3 4 5{
	gen d_prob=skills_t2==`j'
	replace d_prob=. if  skills_t2==.
	qui: sum d_prob if d_prob!=.
	mat beta_aux=r(mean)
	mat prob_inc_t2[`obs',1]=beta_aux[1,1]
	drop d_prob
	local obs=`obs'+1

}



*******************************************************************
/*Identifying period 5 measurement system and prod function*/
********************************************************************

*To identify gammas (production function): 2 x 1 matrix
mat inputs_moments_old=J(2,1,.)
mat inputs_moments_young_cc1=J(3,1,.)

mat sigma_inputs_moments_old=J(2,1,.)
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
	



*Young children/cc=0 and 1: production function




preserve
keep if age_t1<=6
qui: reg skills_t2 d_CC2_t1
mat inputs_moments_young_cc1[3,1]=_b[d_CC2_t1]
restore

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




**********************************************
**********************************************
**********************************************
/*Saving betas*/

mat betas_prod = prob_inc_t2\prob_inc_t5\inputs_moments_old\/*
*/inputs_moments_young_cc1 


program drop input_diff input_theta 


