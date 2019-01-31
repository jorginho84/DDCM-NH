/*
This do-file computes the auxiliary model to identify the parameters of the utility function
*/




****************************************
/*Hours*/
****************************************
preserve

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

qui xi: reg hours_cat2_t i.p_assign if t_ra<=1 
matrix beta_level_hours1=_b[_cons]

qui xi: reg hours_cat3_t i.p_assign if t_ra<=1 
matrix beta_level_hours2=_b[_cons]



restore

*************************
/* Child care choices*/
************************

preserve

reshape long skills_t2 skills_t5 skills_t8 age_t0 d_CC2_t1 d_CC2_t4 /*
*/cc_pay_t1 cc_pay_t4, i(sampleid) j(child) string


gen age_t1=age_t0+1
gen age_t4=age_t0+4

qui xi: reg d_CC2_t1 i.p_assign if age_t1<=5
matrix beta_cc=_b[_cons]


matrix beta_utility = beta_cc\beta_level_hours1\beta_level_hours2

restore

