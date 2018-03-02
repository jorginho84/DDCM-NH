global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills"

clear
program drop _all
clear matrix
clear mata
set maxvar 15000
set more off
set matsize 2000


use "$databases/Youth_original2.dta", clear

*labels
qui: do "$codes/data_youth.do"
keep  sampleid child p_assign zboy agechild p_assign  /*
*/ tq17* /* Y2: SSRS (block1)
*/ tcsbs tcsis tcsts   /* Y2: CBS (block2)*/

/*Local labels: use these in regressions*/
local Y2_B1 tq17a tq17b tq17c tq17d tq17e tq17f tq17g tq17h tq17i tq17j
local Y2_B2 tcsbs tcsis tcsts


*Rounding up variables to the nearest integer
foreach variable of varlist `Y2_B1' `Y2_B2' {
	gen `variable'_s=round(`variable')
	drop `variable'
	rename `variable'_s `variable'
}




*Control variables
qui: do "$codes/skills/Xs.do"

*For young children only!
keep if agechild<=6

tempfile data_aux
save `data_aux', replace


forvalues i=1/2{

	foreach variable of varlist `Y2_B1' `Y2_B2'{ /*These are all oprobits*/
	
	*Same obs per-block here

		if `i'==1{
			qui xi: oprobit `variable' i.p_assign 
		}
		else{
			qui xi: oprobit `variable' i.p_assign age_ra agechild i.marital i.ethnic d_HS higrade i.pastern2
			
		}

		mat T`i'_`variable'=_b[_Ip_assign_2]/_se[_Ip_assign_2]
		local beta_`variable'_`i' = _b[_Ip_assign_2]
	}

	

}

foreach variable of varlist `Y2_B1' `Y2_B2'{
	svmat T1_`variable'
	svmat T2_`variable'
}
keep if _n==1

*Save by model

forvalues x=1/2{
	preserve
	keep T`x'_tq17*
	outsheet using "$results/y2_obs_block1_model`x'.csv", comma replace
	restore

	preserve
	keep T`x'_tcsbs T`x'_tcsis T`x'_tcsts
	outsheet using "$results/y2_obs_block2_model`x'.csv", comma replace
	restore

	
}

*******************************************************
/*Resampled results*/
*******************************************************
set seed 2825
local reps = 1000

*Bootstrapped samples
forvalues x=1/`reps'{
	use `data_aux', clear

	bsample

	forvalues i=1/2{
		foreach variable of varlist `Y2_B1' `Y2_B2'  { /*these are oprobits*/
			
			if `i'==1{
				qui xi: oprobit `variable' i.p_assign
			}
			else{
				qui xi: oprobit `variable' i.p_assign age_ra agechild i.marital i.ethnic d_HS higrade i.pastern2
			}
			
		
			if `x'==1{
				mat T`i'_`variable'=(_b[_Ip_assign_2] - `beta_`variable'_`i'')/_se[_Ip_assign_2]
			}
			else{
				mat T`i'_`variable'=T`i'_`variable'\((_b[_Ip_assign_2] - `beta_`variable'_`i'')/_se[_Ip_assign_2])
			}
			
			
		}

				
	}
	



}


clear
set obs `reps'
foreach variable in `Y2_B1' `Y2_B2'{
	svmat T1_`variable'
	svmat T2_`variable'
}

forvalues x=1/2{
	preserve
	keep T`x'_tq17*
	outsheet using "$results/y2_res_block1_model`x'.csv", comma replace
	restore

	preserve
	keep T`x'_tcsbs T`x'_tcsis T`x'_tcsts
	outsheet using "$results/y2_res_block2_model`x'.csv", comma replace
	restore

	
}


exit, STATA clear



