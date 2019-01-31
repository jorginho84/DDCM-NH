
clear
program drop _all
clear matrix
clear mata
set more off
set maxvar 15000

global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/aux_model" /*this is where I compute aux moments*/


use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear


*these are for anchoring
foreach variable of varlist skills*{
	gen a_`variable'=`variable'>3
	replace a_`variable'=0 if `variable'<=3
	replace a_`variable'=. if `variable'==.
	
}


*these are for pca
foreach variable of varlist skills*{
	gen `variable'_s=`variable'>=3
	replace `variable'_s=0 if `variable'<3
	replace `variable'_s=. if `variable'==.
	

	
}




local y2 skills*_t2_s
local y5 skills*_t5_s
local y8 skills*_t8_s


foreach x of numlist 2 5 8{

	pca `y`x'', components(1)
	predict score yhat`x'
	gen yhat_t`x' = score
	drop score

}

*Anchoring on prob of being in the top 30% (overall)
reg a_skills1_t2 yhat_t2

reg skills1_t2_s yhat_t2
