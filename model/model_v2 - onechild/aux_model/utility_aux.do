/*
This do-file computes the auxiliary model to identify the parameters of the utility function
*/




****************************************
/*Hours*/
****************************************
preserve

*Age of child
gen age_t1=age_t0+1
gen age_t4=age_t0+4

qui: sum d_CC2_t1 if age_t1<=5
matrix beta_cc = r(mean)

drop hours_t0 hours_t1 hours_t4 hours_t7


forvalues x=1/3{
	foreach t of numlist 0 1 4 7{
		rename hours_t`t'_cat`x' hours_cat`x'_t`t'
	}

}

egen id=seq()
keep p_assign id hours_cat*
drop hours_cat1*
reshape long hours_cat2_t hours_cat3_t, i(id) j(t_ra)

qui: sum hours_cat2_t
matrix beta_level_hours1 = r(mean)

qui: sum hours_cat3_t
matrix beta_level_hours2 = r(mean)

matrix beta_utility = beta_cc\beta_level_hours1\beta_level_hours2


restore
