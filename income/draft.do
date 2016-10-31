
foreach school in psub_ ppag_{
	local obs=1
	foreach year_aux in `years'{
		replace `school'effectLB=`wage_m'beta_LB_`school'`year_aux' if _n==`obs'
		replace `school'effectLB_lb=`wage_m'CIlb_LB_`school'`year_aux' if _n==`obs'
		replace `school'effectLB_ub=`wage_m'CIub_LB_`school'`year_aux' if _n==`obs'
		
		replace `school'effectUB=`wage_m'beta_UB_`school'`year_aux' if _n==`obs'
		replace `school'effectUB_lb=`wage_m'CIlb_UB_`school'`year_aux' if _n==`obs'
		replace `school'effectUB_ub=`wage_m'CIub_UB_`school'`year_aux' if _n==`obs'
		local obs=`obs'+1

	}
}



twoway (scatter ppag_effectLB year) (rcap ppag_effectLB_ub ppag_effectLB_lb)/*
*/(scatter ppag_effectUB year) (rcap ppag_effectUB_ub ppag_effectUB_lb)
graph export "$results/impact_earnings_time.pdf", as(pdf) replace
