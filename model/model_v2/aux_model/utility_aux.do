/*
This do-file computes the auxiliary model to identify the parameters of the utility function
*/




use "$results/data_aux.dta", clear

sort sampleid child
*use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear
*Age of child
gen age_t1=age_t0+1
gen age_t4=age_t0+4
gen age_t7=age_t0+7

forvalues x=1/3{
	foreach t of numlist 0 1 4{
		rename hours_t`t'_cat`x' hours_cat`x'_t`t'
	}

}


egen id=seq()
keep age_t0 age_t1 age_t4 hours_cat1* p_assign id
reshape long age_t hours_cat1_t, i(id) j(t_ra)
xtset id t_ra

xi: reg hours_cat1_t i.p_assign if age_t<=5, vce(`SE')
matrix beta_cc=_b[_cons]


****************************************
/*Hours*/
****************************************
use "$results/data_aux.dta", clear
sort sampleid child

drop hours_t0 hours_t1 hours_t4 hours_t7

forvalues x=1/3{
	foreach t of numlist 0 1{
		rename hours_t`t'_cat`x' hours_cat`x'_t`t'
	}

}


egen id=seq()
keep p_assign id hours_cat*
drop hours_cat1*
reshape long hours_cat2_t hours_cat3_t, i(id) j(t_ra)

qui xi: reg hours_cat2_t i.p_assign, vce(`SE')
matrix beta_level_hours2=_b[_Ip_assign_2]

qui xi: reg hours_cat3_t i.p_assign, vce(`SE')
matrix beta_level_hours3=_b[_Ip_assign_2]

matrix beta_utility = beta_cc\beta_level_hours2\beta_level_hours3


