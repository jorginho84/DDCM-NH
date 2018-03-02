/*
This do-file produces a latex table sthat shows the effect of NH on
measures of skills (year 2)
*/

global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills"

/*
robust SE for small samples. Set to hc3 for more conservatives. 

See Angrist and Pischke for more information
"robust" SE can be misleading when the sample size is small and there is no much heteroskedasticity.
*/
local SE="hc2"

*Set # bsamples
local n_boot = 1000

clear
clear matrix
clear mata
scalar drop _all
program drop _all
set seed 100
set maxvar 15000
set more off
set seed 120



use "$databases/Youth_original2.dta", clear
keep  sampleid child p_assign zboy agechild p_assign  /*
*/ tq17* /* Y2: SSRS (block1)
*/ tcsbs tcsis tcsts   /* Y2: CBS (block2)
*/ wjss22 wjss23 wjss24 wjss25 /* Y5: Woodscok-Johnson (block1)
*/ t2q17a t2q17b t2q17c t2q17d t2q17e t2q17f t2q17g t2q17h t2q17i t2q17j /* Y5: SSRS (block2)
*/ t2q16a t2q16b t2q16c t2q16d t2q16e t2q16f /* Y5: mock (block3)
*/ bhvscaf2 trnscaf2 indscaf2 /* Y5: CBS (block4)
*/ piq146a piq146b piq146c piq146d /* Y5: parents' report (block5)
*/ ewjss22 ewjss25 /* Y8: Woodscok-Johnson (block1)
*/ etsq13a etsq13b etsq13c etsq13d etsq13e etsq13f etsq13g etsq13h etsq13i etsq13j /* Y8: teachers reports: SSRS academic subscale (block 2)
*/etsq12a etsq12b etsq12c etsq12d etsq12e etsq12f /* Y8: teachers' reports: mock cards (block3)
*/ bhvscaf3 trnscaf3 indscaf3 /* Y8: teachers' report: classroom behavior scale (block 4)
*/ epi124a epi124b epi124c epi124d /*  Y8: parents' report, school achievement (block 5)*/



*
egen child_id=group(sampleid child)

/*Local labels: use these in regressions*/
local Y2_B1 tq17a tq17b tq17c tq17d tq17e tq17f tq17g tq17h tq17i tq17j
local Y2_B2 tcsbs tcsis tcsts
local Y5_B1 wjss22 wjss23 wjss24 wjss25
local Y5_B2 t2q17a t2q17b t2q17c t2q17d t2q17e t2q17f t2q17g t2q17h t2q17i t2q17j
local Y5_B3 t2q16a t2q16b t2q16c t2q16d t2q16e t2q16f
local Y5_B4 bhvscaf2 trnscaf2 indscaf2
local Y5_B5 piq146a piq146b piq146c piq146d
local Y8_B1 ewjss22 ewjss25
local Y8_B2 etsq13a etsq13b etsq13c etsq13d etsq13e etsq13f etsq13g etsq13h etsq13i etsq13j
local Y8_B3 etsq12a etsq12b etsq12c etsq12d etsq12e etsq12f
local Y8_B4 bhvscaf3 trnscaf3 indscaf3
local Y8_B5 epi124a epi124b epi124c epi124d



*Rounding up variables to the nearest integer
foreach variable of varlist `Y2_B1' `Y2_B2' `Y5_B2' `Y5_B3' `Y5_B5' `Y8_B2' `Y8_B3' `Y8_B5'{
	gen `variable'_s=round(`variable')
	drop `variable'
	rename `variable'_s `variable'
}

*Standardize
foreach variable of varlist `Y5_B4'  `Y8_B4'{
	egen `variable'_s=std(`variable')
	drop `variable'
	rename `variable'_s `variable'
}

*WJ: mean as a population equals 100, and SD=15.
foreach variable of varlist `Y5_B1' `Y8_B1'{
	gen `variable'_st=(`variable'-100)/15
	drop `variable'
	rename `variable'_s `variable'
}


*Control variables
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

label variable tcsbs "Behavior skills"
label variable tcsis "Independent skills"
label variable tcsts "Transitional skills"

*Labels year 5
label variable wjss22 "Letter-Word"
label variable wjss23 "Comprehension"
label variable wjss24 "Calculation"
label variable wjss25 "Applied problems"

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

label variable t2q16a "Reading"
label variable t2q16b "Oral language"
label variable t2q16c "Written language"
label variable t2q16d "Math"
label variable t2q16e "Social studies"
label variable t2q16f "Science"

label variable bhvscaf2 "Behavior skills"
label variable trnscaf2 "Transitional skills"
label variable indscaf2 "Independent skills"

label variable piq146a "Reading"
label variable piq146b "Math"
label variable piq146c "Written work"
label variable piq146d "Overall"

*Label year 8
label variable ewjss22 "Letter-Word"
label variable ewjss25 "Comprehension"

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

label variable etsq12a "Reading" 
label variable etsq12b "Oral language" 
label variable etsq12c "Written language" 
label variable etsq12d "Math" 
label variable etsq12e "Social studies" 
label variable etsq12f "Science" 

label variable bhvscaf3 "Behavior skills"
label variable trnscaf3 "Transitional skills"
label variable indscaf3 "Independent skills"

label variable epi124a "Reading"
label variable epi124b "Math"
label variable epi124c "Written work"
label variable epi124d "Overall"


*Producing statistics for table
gen d_RA = p_assign=="E"
replace d_RA=0 if p_assign=="C"

*******************************************************************
*******************************************************************
*******************************************************************

/*THESE ARE OPROBITS*/
*******************************************************************
*******************************************************************
*******************************************************************
tempfile data_aux
save `data_aux', replace


*Original estimates

foreach variable of varlist `Y2_B1' `Y2_B2' {
	preserve
	qui: keep if `variable'!=.
	qui: count
	local n_`variable'=r(N)
	
	*Baseline
	gen d_30 = `variable'==4 | `variable'==5
	qui: sum d_30 if p_assign=="C"
	local baseline_`variable' = string(round(r(mean),0.001),"%9.3f")

	qui xi: oprobit `variable' d_RA
	qui: predict xbetas, xb
	gen xbetas_tilde = xbetas - _b[d_RA]*d_RA
	gen pr_1 = 1-normal(_b[/cut3]- (xbetas_tilde + _b[d_RA]))
	gen pr_0 = 1-normal(_b[/cut3]- (xbetas_tilde))
	gen dpr = pr_1 - pr_0
	qui: sum dpr
	local beta_model1_orig_`variable'=r(mean)
	local beta_model1_`variable' = string(round(r(mean),0.001),"%9.3f")
	drop xbetas* pr_0 pr_1 dpr


	qui xi: oprobit `variable' d_RA age_ra agechild i.marital i.ethnic d_HS higrade i.pastern2
	qui: predict xbetas, xb
	gen xbetas_tilde = xbetas - _b[d_RA]*d_RA
	gen pr_1 = 1-normal(_b[/cut3]- (xbetas_tilde + _b[d_RA]))
	gen pr_0 = 1-normal(_b[/cut3]- (xbetas_tilde))
	gen dpr = pr_1 - pr_0
	qui: sum dpr
	local beta_model2_orig_`variable' = r(mean)
	local beta_model2_`variable' = string(round(r(mean),0.001),"%9.3f")
	drop xbetas* pr_0 pr_1 dpr



	restore
}




forvalues x=1/`n_boot'{
	foreach variable of varlist `Y2_B1' `Y2_B2' {
		preserve
		qui: keep if `variable'!=.
		bsample


		gen d_30 = `variable'==4 | `variable'==5
		qui xi: oprobit `variable' d_RA
		qui: predict xbetas, xb
		gen xbetas_tilde = xbetas - _b[d_RA]*d_RA
		gen pr_1 = 1-normal(_b[/cut3]- (xbetas_tilde + _b[d_RA]))
		gen pr_0 = 1-normal(_b[/cut3]- (xbetas_tilde))
		gen dpr = pr_1 - pr_0
		qui: sum dpr
		local beta`x'_model1_`variable' = r(mean)
		drop xbetas* pr_0 pr_1 dpr

		qui xi: oprobit `variable' d_RA age_ra agechild i.marital i.ethnic d_HS higrade i.pastern2
		qui: predict xbetas, xb
		gen xbetas_tilde = xbetas - _b[d_RA]*d_RA
		gen pr_1 = 1-normal(_b[/cut3]- (xbetas_tilde + _b[d_RA]))
		gen pr_0 = 1-normal(_b[/cut3]- (xbetas_tilde))
		gen dpr = pr_1 - pr_0
		qui: sum dpr
		local beta`x'_model2_`variable' = r(mean)
		drop xbetas* pr_0 pr_1 dpr


		restore

	}	
}

clear
set obs `n_boot'

foreach variable of newlist `Y2_B1' `Y2_B2'{
	gen beta_model1_`variable' = .
	gen beta_model2_`variable' = .
	
	
	forvalues x=1/`n_boot'{
		qui: replace beta_model1_`variable' = `beta`x'_model1_`variable'' if _n==`x'
		qui: replace beta_model2_`variable' = `beta`x'_model2_`variable'' if _n==`x'
	}

	*Computing pval
	forvalues j=1/2{
		sum beta_model`j'_`variable'
		local beta_mean_`variable' = r(mean)
		gen beta_model`j'_`variable'_dev = (beta_model`j'_`variable'  - r(mean))^2
		egen se_model`j'_`variable' = total(beta_model`j'_`variable'_dev)
		replace se_model`j'_`variable' = (se_model`j'_`variable'/(`n_boot'-1))^.5
		qui: sum se_model`j'_`variable'
		local pval_model`j'_`variable' = 2*(1-normal(abs(`beta_model`j'_orig_`variable''/r(mean))))
		local pval_model`j'_`variable'_aux = string(round(`pval_model`j'_`variable'',0.001),"%9.3f")

	

	}

	
	
}

/*Graph: SSRS*/


clear
set obs 10

forvalues x=1/2{
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

	forvalues x=1/2{
		if `pval_model`x'_`variable''<=0.05{
			replace sig_model`x'_year2=`beta_model`x'_orig_`variable''  if _n==`i'	
		}
		else{
			replace model`x'_year2=`beta_model`x'_orig_`variable''  if _n==`i'		
		}
		
	}
	
	local i = `i' + 1
}


foreach year in 2 {
	local i=1
	foreach variable in `Y`year'_B2'{

		forvalues x=1/2{
			if `pval_model`x'_`variable''<=0.05{
			replace sig_model`x'_year`year'=`beta_model`x'_orig_`variable''  if _n==`i'	
		}
		else{
			replace model`x'_year`year'=`beta_model`x'_orig_`variable''  if _n==`i'		
		}
			
		}
	
	local i = `i' + 1
	}

}

egen id = seq()
reshape long model1_year model2_year sig_model1_year sig_model2_year, i(id) j(year)

forvalues x=1/2{
	twoway (scatter model`x' year, mlcolor(blue) mfcolor(none) msize(large)) /*
	*/ (scatter sig_model`x' year, mlcolor(blue) mfcolor(blue) msize(large)),/*
	*/ legend(off) ytitle("Impact on prob of being in the top 30%")  /*
	*/xtitle("Years after random assignment") /*
	*/ xlabel(2 5 8 , noticks) ylabel(, nogrid)/*
	*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white))/*
	*/ plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white)) scale(1.4)

	graph export "$results/ssrs_model`x'.pdf", as(pdf) replace

}

*******************************************************************
*******************************************************************
*******************************************************************

/*Effects for old and old children*/
*******************************************************************
*******************************************************************
*******************************************************************

use `data_aux', clear

gen d_young = agechild<=6
replace d_young=. if agechild==.

foreach variable of varlist `Y2_B1' `Y2_B2'{
	preserve

	qui: keep if `variable'!=.
	
	
	*Baseline
	gen d_30 = `variable'==4 | `variable'==5
	

	forvalues s = 0/1{/*the sample loop*/
		qui: count if d_young==`s'
		local n_`variable'_`s'=r(N)

		
		qui: sum d_30 if p_assign=="C" & d_young==`s'
		local baseline_`variable'_`s' = string(round(r(mean),0.001),"%9.3f")
		
		*regressions
		qui xi : oprobit `variable' d_RA if d_young==`s'
		qui: predict xbetas if d_young==`s', xb
		gen xbetas_tilde = xbetas - _b[d_RA]*d_RA
		gen pr_1 = 1-normal(_b[/cut3]- (xbetas_tilde + _b[d_RA]))
		gen pr_0 = 1-normal(_b[/cut3]- (xbetas_tilde))
		gen dpr = pr_1 - pr_0
		qui: sum dpr
		local beta_model1_orig_`variable'_`s'=r(mean)
		local beta_model1_`variable'_`s' = string(round(r(mean),0.001),"%9.3f")
		drop xbetas* pr_0 pr_1 dpr

		qui xi: oprobit `variable' d_RA age_ra agechild i.marital i.ethnic d_HS higrade i.pastern2 if d_young==`s'
		qui: predict xbetas if d_young==`s', xb
		gen xbetas_tilde = xbetas - _b[d_RA]*d_RA
		gen pr_1 = 1-normal(_b[/cut3]- (xbetas_tilde + _b[d_RA]))
		gen pr_0 = 1-normal(_b[/cut3]- (xbetas_tilde))
		gen dpr = pr_1 - pr_0
		qui: sum dpr
		local beta_model2_orig_`variable'_`s'=r(mean)
		local beta_model2_`variable'_`s' = string(round(r(mean),0.001),"%9.3f")
		drop xbetas* pr_0 pr_1 dpr
	}


	restore
}

forvalues x=1/`n_boot'{
	foreach variable of varlist `Y2_B1' `Y2_B2'{
		preserve
		bsample
		qui: keep if `variable'!=.

		
		forvalues s = 0/1{

			forvalues nn = 1/5{
				qui: count if `variable'==`nn' & d_young==`s'
				local n_`nn' = r(N)	
			}
			

			if `n_1' != 0 & `n_2' != 0 & `n_3' != 0 & `n_4' != 0 & `n_5' != 0{
				qui xi: oprobit `variable' d_RA if d_young==`s'
				qui: predict xbetas if d_young==`s', xb
				qui{
					gen xbetas_tilde = xbetas - _b[d_RA]*d_RA
					gen pr_1 = 1-normal(_b[/cut3]- (xbetas_tilde + _b[d_RA]))
					gen pr_0 = 1-normal(_b[/cut3]- (xbetas_tilde))
					gen dpr = pr_1 - pr_0
				}
				qui: sum dpr
				local beta`x'_model1_`variable'_`s' = r(mean)
				drop xbetas* pr_0 pr_1 dpr

				qui xi: oprobit `variable' d_RA age_ra agechild i.marital i.ethnic d_HS higrade i.pastern2 if d_young==`s'
				qui: predict xbetas if d_young==`s', xb
				qui{
					gen xbetas_tilde = xbetas - _b[d_RA]*d_RA
					gen pr_1 = 1-normal(_b[/cut3]- (xbetas_tilde + _b[d_RA]))
					gen pr_0 = 1-normal(_b[/cut3]- (xbetas_tilde))
					gen dpr = pr_1 - pr_0	
				}
				
				qui: sum dpr
				local beta`x'_model2_`variable'_`s' = r(mean)
				drop xbetas* pr_0 pr_1 dpr
			}
			else{
				local beta`x'_model1_`variable'_`s' = .
				local beta`x'_model2_`variable'_`s' = .

			}

		}


		restore

	}	
}



forvalues s = 0/1{

	clear
	set obs `n_boot'

	foreach variable of newlist `Y2_B1' `Y2_B2'{
		gen beta_model1_`variable'_`s' = .
		gen beta_model2_`variable'_`s' = .
		
		
		forvalues x=1/`n_boot'{
			qui: replace beta_model1_`variable'_`s' = `beta`x'_model1_`variable'_`s'' if _n==`x'
			qui: replace beta_model2_`variable'_`s' = `beta`x'_model2_`variable'_`s'' if _n==`x'
		}

		*Computing pval
		forvalues j=1/2{
			sum beta_model`j'_`variable'_`s'
			local beta_mean_`variable'_`s' = r(mean)
			gen beta_model`j'_`variable'_`s'_dev = (beta_model`j'_`variable'_`s'  - r(mean))^2
			egen se_model`j'_`variable'_`s' = total(beta_model`j'_`variable'_`s'_dev)
			replace se_model`j'_`variable'_`s' = (se_model`j'_`variable'_`s'/(`n_boot'-1))^.5
			qui: sum se_model`j'_`variable'_`s'
			local pval_model`j'_`variable'_`s' = 2*(1-normal(abs(`beta_model`j'_orig_`variable'_`s''/r(mean))))
			local pval_model`j'_`variable'_`s'_aux = string(round(`pval_model`j'_`variable'_`s'',0.001),"%9.3f")
		

		}
		
		
	}

}


*******************************************************************
*******************************************************************
*******************************************************************

/*Tables*/
*******************************************************************
*******************************************************************
*******************************************************************
use `data_aux', clear

/*Table of Year 2*/
file open Y2 using "$results/Y2_raw.tex", write replace
file write Y2 "\begin{tabular}{llccccccc}"_n
file write Y2 "\hline"_n
file write Y2 "\multirow{2}[2]{*}{\textbf{Measure}} &       & \multirow{2}[2]{*}{\textbf{Baseline}} &       & \multicolumn{2}{c}{\textbf{Model 1}} &       & \multicolumn{2}{c}{\textbf{Model 2}} \bigstrut[t]\\"_n
file write Y2 "      &       &       &       & \textbf{Estimate} & \textbf{p-value} &       & \textbf{Estimate} & \multicolumn{1}{c}{\textbf{p-value}} \bigstrut[b]\\"_n
file write Y2 "\cline{1-1}\cline{3-3}\cline{5-6}\cline{8-9}      &       &       &       &       &       &       &       &  \bigstrut[t]\\"_n
file write Y2 "\multicolumn{5}{l}{\textbf{Panel A. SSRS Academic Subscale}} &       &       &       &  \\"_n
*write here the loop:
foreach variable in `Y2_B1' {
	local lab: variable label `variable'
	file write Y2 "`lab' (\$n=`n_`variable''\$) &       & `baseline_`variable'' & "
	
	if `pval_model1_`variable''<0.05{
		file write Y2 "      & \textbf{`beta_model1_`variable''} & `pval_model1_`variable'_aux' & "
	}
	else{
		file write Y2 "      & `beta_model1_`variable'' & `pval_model1_`variable'_aux' & "
	}
	
	if `pval_model2_`variable''<0.05{
		file write Y2 "      & \textbf{`beta_model2_`variable''} & `pval_model2_`variable'_aux' \\ " _n
	}
	else{
		file write Y2 "      & `beta_model2_`variable'' & `pval_model2_`variable'_aux' \\ " _n
	}


}

file write Y2 ""_n
file write Y2 "\multicolumn{5}{l}{\textbf{Panel B. Classroom Behavior Scale}} &       &       &       &  \\"_n
foreach variable in `Y2_B2' {
	local lab: variable label `variable'
	file write Y2 "`lab' (\$n=`n_`variable''\$) &       & `baseline_`variable'' & "
	
	if `pval_model1_`variable''<0.05{
		file write Y2 "      & \textbf{`beta_model1_`variable''} & `pval_model1_`variable'_aux' & "
	}
	else{
		file write Y2 "      & `beta_model1_`variable'' & `pval_model1_`variable'_aux' & "
	}
	
	if `pval_model2_`variable''<0.05{
		file write Y2 "      & \textbf{`beta_model2_`variable''} & `pval_model2_`variable'_aux' \\ " _n
	}
	else{
		file write Y2 "      & `beta_model2_`variable'' & `pval_model2_`variable'_aux' \\ " _n
	}
}

file write Y2 "\hline"_n
file write Y2 "\end{tabular}"_n
file close Y2


*************************************************************
*Tables of year 2 by age of child

*************************************************************

forvalues s = 0/1{
	file open Y2 using "$results/Y2_`s'_raw.tex", write replace
	file write Y2 "\begin{tabular}{llccccccc}"_n
	file write Y2 "\hline"_n
	file write Y2 "\multirow{2}[2]{*}{\textbf{Measure}} &       & \multirow{2}[2]{*}{\textbf{Baseline}} &       & \multicolumn{2}{c}{\textbf{Model 1}} &       & \multicolumn{2}{c}{\textbf{Model 2}} \bigstrut[t]\\"_n
	file write Y2 "      &       &       &       & \textbf{Estimate} & \textbf{p-value} &       & \textbf{Estimate} & \multicolumn{1}{c}{\textbf{p-value}} \bigstrut[b]\\"_n
	file write Y2 "\cline{1-1}\cline{3-3}\cline{5-6}\cline{8-9}      &       &       &       &       &       &       &       &  \bigstrut[t]\\"_n
	file write Y2 "\multicolumn{5}{l}{\textbf{Panel A. SSRS Academic Subscale}} &       &       &       &  \\"_n
	*write here the loop:
	foreach variable in `Y2_B1' {
		local lab: variable label `variable'
		file write Y2 "`lab' (\$n=`n_`variable'_`s''\$) &       & `baseline_`variable'_`s'' & "
		
		if `pval_model1_`variable'_`s''<0.05{
			file write Y2 "      & \textbf{`beta_model1_`variable'_`s''} & `pval_model1_`variable'_`s'_aux' & "
		}
		else{
			file write Y2 "      & `beta_model1_`variable'_`s'' & `pval_model1_`variable'_`s'_aux' & "
		}
		
		if `pval_model2_`variable'_`s''<0.05{
			file write Y2 "      & \textbf{`beta_model2_`variable'_`s''} & `pval_model2_`variable'_`s'_aux' \\ " _n
		}
		else{
			file write Y2 "      & `beta_model2_`variable'_`s'' & `pval_model2_`variable'_`s'_aux' \\ " _n
		}


	}

	file write Y2 ""_n
	file write Y2 "\multicolumn{5}{l}{\textbf{Panel B. Classroom Behavior Scale}} &       &       &       &  \\"_n
	foreach variable in `Y2_B2' {
		local lab: variable label `variable'
		file write Y2 "`lab' (\$n=`n_`variable'_`s''\$) &       & `baseline_`variable'_`s'' & "
		
		if `pval_model1_`variable'_`s''<0.05{
			file write Y2 "      & \textbf{`beta_model1_`variable'_`s''} & `pval_model1_`variable'_`s'_aux' & "
		}
		else{
			file write Y2 "      & `beta_model1_`variable'_`s'' & `pval_model1_`variable'_`s'_aux' & "
		}
		
		if `pval_model2_`variable'_`s''<0.05{
			file write Y2 "      & \textbf{`beta_model2_`variable'_`s''} & `pval_model2_`variable'_`s'_aux' \\ " _n
		}
		else{
			file write Y2 "      & `beta_model2_`variable'_`s'' & `pval_model2_`variable'_`s'_aux' \\ " _n
		}
	}

	file write Y2 "\hline"_n
	file write Y2 "\end{tabular}"_n
	file close Y2

}
