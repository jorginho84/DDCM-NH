/*
This do-file computes the auxiliary model to identify the parameters of the utility function
*/


global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/aux_model"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"

/*
robust SE for small samples. Set to hc3 for more conservatives. 

See Angrist and Pischke for more information
"robust" SE can be misleading when the sample size is small and there is no much heteroskedasticity.
*/
local SE="hc2"

clear
clear matrix
clear mata
set more off
set maxvar 15000


****************************************
/*Child care at period t=1 and t=4*/
****************************************
use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear


*Age of child
gen age_t1=age_t0+1
gen age_t4=age_t0+4
gen age_t7=age_t0+7

egen id=group(sampleid child)
keep age_t1 age_t4 d_CC2_t1  d_CC2_t4 p_assign id
reshape long age_t d_CC2_t, i(id) j(t_ra)
xtset id t_ra

xi: reg d_CC2_t i.p_assign if age_t<=5, vce(`SE')
matrix beta=_b[_Ip_assign_2]\_b[_cons]
matrix sigma_aux=e(V)
matrix sigma=sigma_aux[1,1]\sigma_aux[2,2]
svmat beta
svmat sigma

preserve
keep beta*
drop if beta1==.
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/beta_childcare_v2.csv", comma  replace
restore

preserve
keep sigma*
drop if sigma1==.
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_childcare_v2.csv", comma replace
restore

****************************************
/*Hours*/
****************************************
use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear
drop hours_t0 hours_t1 hours_t4 hours_t7

forvalues x=1/3{
	foreach t of numlist 0 1 4 7{
		rename hours_t`t'_cat`x' hours_cat`x'_t`t'
	}

}


egen id=group(sampleid child)
keep p_assign id hours_cat*
drop hours_cat1*
reshape long hours_cat2_t hours_cat3_t, i(id) j(t_ra)

qui xi: reg hours_cat2_t i.p_assign, vce(`SE')
matrix beta_hours2=_b[_Ip_assign_2]
matrix sigma_hours2_aux=e(V)
matrix sigma_hours2=sigma_hours2_aux[1,1]
matrix beta_level_hours2=_b[_cons]
matrix sigma_level_hours2=sigma_hours2_aux[2,2]



qui xi: reg hours_cat3_t i.p_assign, vce(`SE')
matrix beta_hours3=_b[_Ip_assign_2]
matrix sigma_hours3_aux=e(V)
matrix sigma_hours3=sigma_hours3_aux[1,1]
matrix beta_level_hours3=_b[_cons]
matrix sigma_level_hours3=sigma_hours3_aux[2,2]

svmat beta_hours2
svmat sigma_hours2
svmat beta_level_hours2
svmat sigma_level_hours2
svmat beta_hours3
svmat sigma_hours3
svmat beta_level_hours3
svmat sigma_level_hours3

tempfile param
save `param', replace

forvalues x=2/3{
	use `param', clear
	keep beta_hours`x' 
	drop if beta_hours`x'1==.
	outsheet using "$results/aux_model/beta_hours`x'_v2.csv", comma  replace

	use `param', clear
	keep sigma_hours`x'*
	drop if sigma_hours`x'1==.
	outsheet using "$results/aux_model/sigma_hours`x'_v2.csv", comma  replace
	
	use `param', clear
	keep beta_level_hours`x' 
	drop if beta_level_hours`x'1==.
	outsheet using "$results/aux_model/beta_level_hours`x'_v2.csv", comma  replace
	
	use `param', clear
	keep sigma_level_hours`x'*
	drop if sigma_level_hours`x'1==.
	outsheet using "$results/aux_model/sigma_level_hours`x'_v2.csv", comma  replace

}



/*
Mean hours by period t=1,2,3, categories 1,2,3

use `param', clear
forvalues t=0/3{
	sum hours_t`t'_cat1
	mat ht`t'=r(mean)
	sum hours_t`t'_cat2
	mat ht`t'=ht`t'\r(mean)
	sum hours_t`t'_cat3
	mat ht`t'=ht`t'\r(mean)
	
}

svmat ht0
svmat ht1
svmat ht2
svmat ht3
preserve
keep ht*
drop if ht11==.
outsheet using "$results/aux_model/hours_mean_v2.csv", comma  replace

*/
