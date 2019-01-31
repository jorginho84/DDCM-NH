use "/home/jrodriguez/NH_HC/results/Model/sample_model.dta", clear



*Correlation between ssrs2 measures

foreach ch in "A" "B"{
	gen d_skills_t2`ch' = skills_t2`ch'>3
	replace d_skills_t2`ch' = 0 if skills_t2`ch'<=3	
}


corr d_skills_t2A d_skills_t2B if p_assign=="C"
mat betas_corr = r(rho)

drop d_skills_t2A d_skills_t2B
*************************************************************************
*Reshaping to long form
reshape long skills_t2 skills_t5 skills_t8 age_t0 d_CC2_t1 d_CC2_t4 /*
*/cc_pay_t1 cc_pay_t4, i(sampleid) j(child) string

*Indicates prescence of child
gen d_child = age_t0 !=.

*Nobody in child care at t=7
gen d_CC2_t7 = 0

*Age of child
gen age_t1=age_t0+1
gen age_t4=age_t0+4
gen age_t7=age_t0+7

*Standardized measures
foreach x of numlist 2 5 8{
	rename skills_t`x' skills_t`x'_aux
	egen skills_t`x'=std(skills_t`x'_aux)
}

*Dummies
foreach x of numlist 2 5 8{
	gen d_skills_t`x' = .
	replace d_skills_t`x' = 1 if skills_t`x'_aux > 3
	replace d_skills_t`x' = 0 if skills_t`x'_aux <= 3
	replace d_skills_t`x' = . if skills_t`x'_aux == .
}



*Time outside market
foreach x of numlist 1 4 7{
	gen l_t`x' = .
	replace l_t`x' = (168-hours_t`x') if d_CC2_t`x'==0 & age_t`x'<=6
	replace l_t`x' = (168-40) if d_CC2_t`x'==1 & age_t`x'<=6
	replace l_t`x' = (133-hours_t`x') if age_t`x'>6
}

*Income
gen incomepc_t1 = (total_income_y1 -cc_pay_t1*12)/(1 + nkids_year2 + married_year2)
gen incomepc_t4 = (total_income_y4-cc_pay_t4*12)/(1 + nkids_year5 + married_year5)
gen incomepc_t7 = (total_income_y7)/(1 + nkids_year8 + married_year8)

replace incomepc_t1 = 0 if incomepc_t1 < 0
replace incomepc_t4 = 0 if incomepc_t4 < 0
replace incomepc_t7 = 0 if incomepc_t7 < 0




/*Initial conditions*/
mat betas_init=J(1,1,.)

foreach x of numlist 0 {
	replace grossv2_y`x'=grossv2_y`x'/52
}


*Hourly wages
foreach x of numlist 0 {
	gen hwage_t`x'=grossv2_y`x'/hours_t`x'
}

gen lhwage_t0=log(hwage_t0)



**********************************************************************************************
**********************************************************************************************
**********************************************************************************************

*Inconditional Probs: matrix of 4 (categories) X 1 (measures)
*(to identify kappas)
matrix prob_inc_t2=J(4,1,.)
local obs=1
foreach j of numlist 2 3 4 5{
	gen d_prob=skills_t2_aux==`j'
	replace d_prob=. if  skills_t2==.
	qui: sum d_prob if d_prob!=. & p_assign=="C" & d_child == 1
	mat beta_aux=r(mean)
	mat prob_inc_t2[`obs',1]=beta_aux[1,1]
	drop d_prob
	local obs=`obs'+1
}

matrix prob_inc_t5=J(4,1,.)
local jj=1
foreach j of numlist 2 3 4 5{
	gen d_prob=skills_t5_aux==`j'
	replace d_prob=. if  skills_t5==.
	sum d_prob if d_prob!=. & p_assign=="C" & d_child == 1
	mat prob_inc_t5[`jj',1]=r(mean)
	drop d_prob
	local jj=`jj'+1
}




*******************************************************************
/*Identifying period 5 measurement system and prod function*/
********************************************************************

*To identify gammas (production function): 2 x 1 matrix
mat inputs_moments=J(5,1,.)

corr skills_t2  lhwage_t0 if p_assign=="C" & d_child == 1
mat inputs_moments[5,1] = r(rho)

corr skills_t2 skills_t5 if p_assign == "C" & d_child == 1
mat inputs_moments[1,1] = r(rho)



egen id_child = seq()

*Adjust them for panel data
foreach x of numlist 2 5 8{
	local z = `x' - 1
	rename skills_t`x' skills_t`z'
	rename d_skills_t`x' d_skills_t`z'

}

keep incomepc_t1 incomepc_t4 incomepc_t7 skills_t1 skills_t4 skills_t7 /*
*/ l_t1 l_t4 l_t7 d_CC2_t1 d_CC2_t4 d_CC2_t7 /*
*/ id_child age_t1 age_t4 age_t7 d_skills_t1 d_skills_t4 d_skills_t7 p_assign d_child

reshape long incomepc_t skills_t d_skills_t l_t d_CC2_t age_t, i(id_child) j(year)

bysort year: corr d_skills_t incomepc_t if p_assign=="C"
bysort year: corr d_skills_t l_t if p_assign=="C"

reg d_skills_t incomepc_t l_t if p_assign=="C" & year<7 & d_child == 1
mat inputs_moments[2,1] = _b[incomepc_t]
mat inputs_moments[3,1] = _b[l_t]

reg d_skills_t d_CC2_t if age_t<=5 & p_assign=="C" & year<7 & d_child == 1
mat inputs_moments[4,1] = _b[d_CC2_t]



**********************************************
**********************************************
**********************************************
/*Saving betas*/

matrix betas_theta =prob_inc_t2\prob_inc_t5\inputs_moments\betas_corr

