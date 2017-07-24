/*
This file produces impact on SSRS by age or employment at baseline

*/

global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/HH_summary"

/*
robust SE for small samples. Set to hc3 for more conservatives. 

See Angrist and Pischke for more information
"robust" SE can be misleading when the sample size is small and there is no much heteroskedasticity.
*/
local SE="hc2"

*Set # bsamples
local reps=1000

clear
clear matrix
clear mata
scalar drop _all
program drop _all
set seed 100
set maxvar 15000
set more off


/*
0: show results by employment at baseline
1: show results by age
*/

local het = 1

use "$databases/Youth_original2.dta", clear
keep  sampleid child p_assign zboy agechild p_assign  /*
*/ tq17* /* Y2: SSRS (block1)
*/ t2q17a t2q17b t2q17c t2q17d t2q17e t2q17f t2q17g t2q17h t2q17i t2q17j /* Y5: SSRS (block2)
*/ etsq13a etsq13b etsq13c etsq13d etsq13e etsq13f etsq13g etsq13h etsq13i etsq13j /* Y8: teachers reports: SSRS academic subscale (block 2)*/

egen child_id=group(sampleid child)

/*Local labels: use these in regressions*/
local Y2_B1 tq17a tq17b tq17c tq17d tq17e tq17f tq17g tq17h tq17i tq17j
local Y5_B2 t2q17a t2q17b t2q17c t2q17d t2q17e t2q17f t2q17g t2q17h t2q17i t2q17j
local Y8_B2 etsq13a etsq13b etsq13c etsq13d etsq13e etsq13f etsq13g etsq13h etsq13i etsq13j

foreach variable of varlist `Y2_B1' `Y5_B2' `Y8_B2'{
	gen `variable'_s=round(`variable')
	drop `variable'
	rename `variable'_s `variable'
}


*The rank measures to dummy variables
foreach variable of varlist `Y2_B1' `Y5_B2' `Y8_B2'{
	gen `variable'_d = `variable'>=3
	replace `variable'_d=0 if `variable'<3
	drop `variable'
	rename `variable'_d `variable'

}

qui: do "$codes/skills/Xs.do"

*Labels year 2
label variable tq17a "Overall"
label variable tq17b "Reading"
label variable tq17c "Math"
label variable tq17d "Reading grade expectations"
label variable tq17e "Math grade expectations"
label variable tq17f "Motivation"
label variable tq17g "Parental encouragement"
label variable tq17h "Intellectual functioning"
label variable tq17i "Classroom behavior"
label variable tq17j "Communication skills"

label variable t2q17a "Overall"
label variable t2q17b "Reading"
label variable t2q17c "Math"
label variable t2q17d "Reading grade expectations"
label variable t2q17e "Math grade expectations"
label variable t2q17f "Motivation"
label variable t2q17g "Parental encouragement"
label variable t2q17h "Intellectual functioning"
label variable t2q17i "Class behavior"
label variable t2q17j "Communication skills"

label variable etsq13a "Overall"
label variable etsq13b "Reading"
label variable etsq13c "Math"
label variable etsq13d "Reading grade expectations"
label variable etsq13e "Math grade expectations"
label variable etsq13f "Motivation"
label variable etsq13g "Parental encouragement"
label variable etsq13h "Intellectual functioning"
label variable etsq13i "Class behavior"
label variable etsq13j "Communication skills"

*Loop by age: less than 6 in the last year of the program

if `het' == 0{
	gen d_sample = 1 if emp_baseline==1
	replace d_sample=0 if emp_baseline==0

}
else{
	gen d_sample = 1 if agechild<=6
	replace d_sample=0 if agechild>6

}


*RA indicator
gen d_RA =1 if p_assign=="E"
replace d_RA=0 if p_assign=="C"


forvalues x=0/1{/*old,young*/

	foreach variable of varlist `Y2_B1' `Y5_B2' `Y8_B2'{

		preserve
		qui: keep if `variable'!=.
		qui: count
		local n_`variable'=r(N)
	

		qui: reg `variable' i.d_RA age_ra agechild i.marital i.ethnic d_HS higrade i.pastern2 if d_sample==`x'
		local pval_model`x'_`variable'_aux = 2*(1-normal(abs(_b[1.d_RA]/_se[1.d_RA])))
		local pval_model`x'_`variable' = string(round(`pval_model`x'_`variable'_aux',0.001),"%9.3f")
		local beta_model`x'_`variable' = string(round(_b[1.d_RA],0.001),"%9.3f")
		

		restore




	}



}




*****************************************************************************************
/*Graph: SSRS*/

preserve
clear
set obs 10

forvalues x=0/1{
	gen model`x'_year2=.
	gen sig_model`x'_year2=.
	gen model`x'_year5=.
	gen sig_model`x'_year5=.
	gen model`x'_year8=.
	gen sig_model`x'_year8=.


}

*Recovering values
local i=1
foreach variable in `Y2_B1'{

	forvalues x=0/1{
		if `pval_model`x'_`variable''<=0.05{
			replace sig_model`x'_year2=`beta_model`x'_`variable''  if _n==`i'	
		}
		else{
			replace model`x'_year2=`beta_model`x'_`variable''  if _n==`i'		
		}
		
	}
	
	local i = `i' + 1
}


foreach year in 5 8{
	local i=1
	foreach variable in `Y`year'_B2'{

		forvalues x=0/1{
			if `pval_model`x'_`variable''<=0.05{
			replace sig_model`x'_year`year'=`beta_model`x'_`variable''  if _n==`i'	
		}
		else{
			replace model`x'_year`year'=`beta_model`x'_`variable''  if _n==`i'		
		}
			
		}
	
	local i = `i' + 1
	}
}



egen id = seq()
reshape long model0_year model1_year sig_model0_year sig_model1_year, i(id) j(year)

*Set labels

if `het'==0{
	local sample_1 "Employed"
	local sample_0 "Unemployed"
	local name_g "employment"
}
else{
	local sample_1 "Young"
	local sample_0 "Old"
	local name_g "age"

}

twoway (scatter model1 year, mlcolor(blue) mfcolor(none) msize(large)) /*
*/ (scatter sig_model1 year, mlcolor(blue) mfcolor(blue) msize(large))/*
*/ (scatter model0 year, mlcolor(red) mfcolor(none) msize(large)) /*
*/ (scatter sig_model0 year, mlcolor(red) mfcolor(red) msize(large)),/*
*/ ytitle("Impact on prob of being in the top 30%")  /*
*/ xtitle("Years after random assignment") /*
*/ legend(order(1 "`sample_1'" 3 "`sample_0'")  )/*
*/ xlabel(2 5 8 , noticks) ylabel(, nogrid)/*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white))/*
*/ plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white)) scale(1.3)

graph export "$results/ssrs_`name_g'.pdf", as(pdf) replace



restore





