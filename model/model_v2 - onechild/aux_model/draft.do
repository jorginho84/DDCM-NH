use "/home/jrodriguez/NH_HC/results/model_v2/sample_model.dta", clear

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

/*Intercepts and variances*/

matrix prob_inc_t2=J(1,1,.)
qui: sum skills_t2
matrix prob_inc_t2[1,1] =r(mean)


matrix prob_inc_t5=J(1,1,.)
qui: sum skills_t5
matrix prob_inc_t5[1,1] =r(mean)




*******************************************************************
/*Identifying period 5 measurement system and prod function*/
********************************************************************

*To identify gammas (production function): 2 x 1 matrix
mat inputs_moments = J(4,1,.)

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
*/ total_income_y1 total_income_y4 total_income_y7

reshape long incomepc_t skills_t d_skills_t l_t d_CC2_t age_t hours2_t total_income_y, i(id_child) j(year)

gen l_incomepc_t = ln(incomepc_t)
gen l_l_t = ln(l_t)

replace incomepc_t = incomepc_t/1000
replace l_t = l_t/1000

*reg skills_t incomepc_t hours2_t if p_assign=="C" & year<7

corr skills_t total_income_y if year<7


corr skills_t hours2_t if year<7


reg skills_t d_CC2_t if age_t<=5 & year<7

gen l_skills_t = log(skills_t)
gen l_total_income_y = log(total_income_y + 1)
gen l_total_income_y_2 = l_total_income_y^2
gen l_hours2_t = log(hours2_t + 1)
gen l_hours2_t_2 = l_hours2_t^2
gen l_total_income_y_l_hours2_t = l_total_income_y*l_hours2_t


reg l_skills_t l_total_income_y l_total_income_y_2 l_hours2_t l_hours2_t_2 l_total_income_y_l_hours2_t if year < 7


