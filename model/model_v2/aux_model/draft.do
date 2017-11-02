

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
*Time outside market
foreach x of numlist 1 4 {
	gen l_t`x'=.
	if d_CC2_t`x'==0{
		replace l_t`x'=(148-hours_t`x') 	
	}
	else{
		replace l_t`x'=(148-40)

	}
	

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


/*Initial conditions*/
mat betas_init=J(6,1,.)

foreach x of numlist 0 {
	replace grossv2_y`x'=grossv2_y`x'/52
}


*Hourly wages
foreach x of numlist 0 {
	gen hwage_t`x'=grossv2_y`x'/hours_t`x'
}

gen lhwage_t0=log(hwage_t0)


reg yhat_t2 married_y0
mat betas_init[3,1] = _b[married_y0]

corr yhat_t2 nkids_baseline 
mat betas_init[4,1] = r(rho)

reg yhat_t2 d_HS2 
mat betas_init[5,1] = _b[d_HS2]

reg yhat_t2 age_ra age_ra2
mat betas_init[1,1] = _b[age_ra]
mat betas_init[2,1] = _b[age_ra2]

corr yhat_t2 lhwage_t0 
mat betas_init[6,1] = r(rho)

stop

*******************************************************************
/*Identifying  prod function*/
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

matrix betas_theta = betas_prod\betas_init

