/*
This do-file computes the auxiliary model to identify the parameters of the 
production function
*/


use "$results/data_aux.dta", clear


*PCA measures

foreach variable of varlist skills*{
	gen `variable'_s=`variable'>=3
	replace `variable'_s=0 if `variable'<3
	replace `variable'_s=. if `variable'==.
	drop `variable'
	rename `variable'_s `variable'

}

local y2 skills*_t2
local y5 skills*_t5
local y8 skills*_t8


foreach x of numlist 2 5 8{

	pca `y`x'', components(1)
	predict score yhat`x'
	gen yhat_t`x' = score
	drop score

}


*Time outside market
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


*******************************************************************
/*Identifying period 5 measurement system and prod function*/
********************************************************************
mat betas_prod=J(5,1,.)

corr yhat_t2 yhat_t5
mat betas_prod[1,1] = r(rho)


egen id_child = seq()
rename yhat_t2 yhat_t1
rename yhat_t5 yhat_t4

keep incomepc_t1 incomepc_t4 yhat_t1 yhat_t4 l_t1 l_t4 d_CC2_t1 d_CC2_t4 id_child age_t1 age_t4 

reshape long incomepc_t yhat_t l_t d_CC2_t age_t, i(id_child) j(year)

corr yhat_t incomepc_t
mat betas_prod[2,1] = r(rho)

corr yhat_t l_t
mat betas_prod[3,1] = r(rho)

reg yhat_t d_CC2_t if age_t<=6
mat betas_prod[4,1] = _b[d_CC2_t]

sum yhat_t
mat betas_prod[5,1] = r(Var)


