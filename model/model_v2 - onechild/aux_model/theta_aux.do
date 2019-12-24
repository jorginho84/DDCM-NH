/*
This do-file computes the auxiliary model to identify the parameters of the 
production function
*/


preserve

*This if full-time work
local hours_f = 40

*Nobody in child care at t=7
gen d_CC2_t7 = 0

*Age of child
gen age_t1=age_t0+1
gen age_t4=age_t0+4
gen age_t7=age_t0+7


*Time outside market
foreach x of numlist 1 4 7{
	gen hours2_t`x' = .
	replace hours2_t`x' = 0 if hours_t`x'_cat1 == 1
	replace hours2_t`x' = 15 if hours_t`x'_cat2 == 1
	replace hours2_t`x' = 40 if hours_t`x'_cat3 == 1

	gen l_t`x'=.
	replace l_t`x'=(168-hours2_t`x') if d_CC2_t`x'==0 & age_t`x'<=5
	replace l_t`x'=(168-`hours_f') if d_CC2_t`x'==1 & age_t`x'<=5
	replace l_t`x'=(133-hours2_t`x') if age_t`x'>5
}

*Income
gen incomepc_t1 = (total_income_y1)/(1 + nkids_year2 + married_year2)
gen incomepc_t4 = (total_income_y4)/(1 + nkids_year5 + married_year5)
gen incomepc_t7 = (total_income_y7)/(1 + nkids_year8 + married_year8)

replace incomepc_t1 = 1 if incomepc_t1 <= 0
replace incomepc_t4 = 1 if incomepc_t4 <= 0
replace incomepc_t7 = 1 if incomepc_t7 <= 0




/*Initial conditions*/
mat betas_init=J(1,1,.)

foreach x of numlist 0 {
	replace grossv2_y`x'=grossv2_y`x'/52
}


*Hourly wages
foreach x of numlist 0 {
	gen hwage_t`x'=grossv2_y`x'/hours_t`x'
}

gen lhwage_t0=ln(hwage_t0)


*******************************************************************
/*Identifying period 5 measurement system and prod function*/
********************************************************************

*To identify gammas (production function): 2 x 1 matrix
mat inputs_moments = J(6,1,.)

mat init_prod = J(1,1,.)

corr skills_t2 skills_t5
mat inputs_moments[1,1] = r(rho)

corr skills_t2  lhwage_t0
mat init_prod[1,1] = r(rho)

egen id_child = seq()

*Adjust them for panel data
foreach x of numlist 2 5 8{
	local z = `x' - 1
	rename skills_t`x' skills_t`z'
	
}

keep incomepc_t1 incomepc_t4 incomepc_t7 skills_t1 skills_t4 skills_t7 /*
*/ l_t1 l_t4 l_t7 d_CC2_t1 d_CC2_t4 d_CC2_t7 hours2_t1 hours2_t4 hours2_t7/*
*/ id_child age_t1 age_t4 age_t7 p_assign /*
*/ total_income_y1 total_income_y4 total_income_y7 d_HS2

reshape long incomepc_t skills_t d_skills_t l_t d_CC2_t age_t hours2_t total_income_y, i(id_child) j(year)

replace incomepc_t = incomepc_t/1000

*reg skills_t incomepc_t hours2_t if p_assign=="C" & year<7


replace total_income_y = total_income_y/100000
replace hours2_t = hours2_t/100

reg skills_t total_income_y hours2_t if year<7 
mat inputs_moments[2,1] = _b[total_income_y]
mat inputs_moments[3,1] = _b[hours2_t]


reg skills_t d_CC2_t if age_t<=5 & year<7
mat inputs_moments[4,1] = _b[d_CC2_t]


sum skills_t if year == 1
mat inputs_moments[5,1] = r(Var)

sum skills_t if year == 4
mat inputs_moments[6,1] = r(Var)





**********************************************
**********************************************
**********************************************
/*Saving betas*/

matrix betas_theta = inputs_moments\init_prod

restore

