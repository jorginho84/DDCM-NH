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
local reps=1000

clear
clear matrix
clear mata
scalar drop _all
program drop _all
set seed 100
set maxvar 15000
set more off

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

/*These are oprobits*/
foreach variable of varlist `Y2_B1' `Y2_B2' `Y5_B2' `Y5_B3' `Y5_B5' `Y8_B2' `Y8_B3' `Y8_B5'{ 
	

	preserve
	qui: keep if `variable'!=.
	qui: count
	local n_`variable'=r(N)
	
	*Baseline
	gen d_30 = `variable'==4 | `variable'==5
	qui: sum d_30 if p_assign=="C"
	local baseline_`variable' = string(round(r(mean),0.001),"%9.3f")

	*Model 1
	qui: oprobit `variable' i.d_RA
	local pval_model1_`variable'_aux = 2*(1-normal(abs(_b[1.d_RA]/_se[1.d_RA])))
	local pval_model1_`variable' = string(round(`pval_model1_`variable'_aux',0.001),"%9.3f")
	predict xbetas, xb
	gen xbetas_tilde = xbetas - _b[1.d_RA]*d_RA
	gen pr_1 = 1-normal(_b[/cut3]- (xbetas_tilde + _b[1.d_RA]))
	gen pr_0 = 1-normal(_b[/cut3]- (xbetas_tilde))
	gen dpr = pr_1 - pr_0
	qui: sum dpr
	local beta_model1_`variable' = string(round(r(mean),0.001),"%9.3f")
	drop xbetas* pr_0 pr_1 dpr


	*Model 2
	qui: oprobit `variable' i.d_RA age_ra agechild i.marital i.ethnic d_HS higrade i.pastern2
	local pval_model2_`variable'_aux = 2*(1-normal(abs(_b[1.d_RA]/_se[1.d_RA])))
	local pval_model2_`variable' = string(round(`pval_model2_`variable'_aux',0.001),"%9.3f")
	predict xbetas, xb
	gen xbetas_tilde = xbetas - _b[1.d_RA]*d_RA
	gen pr_1 = 1-normal(_b[/cut3]- (xbetas_tilde + _b[1.d_RA]))
	gen pr_0 = 1-normal(_b[/cut3]- (xbetas_tilde))
	gen dpr = pr_1 - pr_0
	qui: sum dpr
	local beta_model2_`variable' = string(round(r(mean),0.001),"%9.3f")
	drop xbetas* pr_0 pr_1 dpr

	restore
	

}


/*These are OLS*/
foreach variable of varlist `Y5_B1' `Y5_B4' `Y8_B1' `Y8_B4'{ 
	

	preserve
	qui: keep if `variable'!=.
	qui: count
	local n_`variable'=r(N)
	
	*Baseline
	qui: sum `variable' if p_assign=="C"
	local baseline_`variable' = string(round(r(mean),0.001),"%9.3f")

	*Model 1
	qui: regress `variable' i.d_RA
	local pval_model1_`variable'_aux = 2*(1-normal(abs(_b[1.d_RA]/_se[1.d_RA])))
	local pval_model1_`variable' = string(round(`pval_model1_`variable'_aux',0.001),"%9.3f")
	local beta_model1_`variable' = string(round(_b[1.d_RA],0.001),"%9.3f")
	
	*Model 2
	qui: regress `variable' i.d_RA age_ra agechild i.marital i.ethnic d_HS higrade i.pastern2
	local pval_model2_`variable'_aux = 2*(1-normal(abs(_b[1.d_RA]/_se[1.d_RA])))
	local pval_model2_`variable' = string(round(`pval_model2_`variable'_aux',0.001),"%9.3f")
	local beta_model2_`variable' = string(round(_b[1.d_RA],0.001),"%9.3f")
	
	restore
	

}


*******************************************************
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
	
	if `pval_model1_`variable'_aux'<0.05{
		file write Y2 "      & \textbf{`beta_model1_`variable''} & `pval_model1_`variable'' & "
	}
	else{
		file write Y2 "      & `beta_model1_`variable'' & `pval_model1_`variable'' & "
	}
	
	if `pval_model2_`variable'_aux'<0.05{
		file write Y2 "      & \textbf{`beta_model2_`variable''} & `pval_model2_`variable'' \\ " _n
	}
	else{
		file write Y2 "      & `beta_model2_`variable'' & `pval_model2_`variable'' \\ " _n
	}


}

file write Y2 ""_n
file write Y2 "\multicolumn{5}{l}{\textbf{Panel B. Classroom Behavior Scale}} &       &       &       &  \\"_n
foreach variable in `Y2_B2' {
	local lab: variable label `variable'
	file write Y2 "`lab' (\$n=`n_`variable''\$) &       & `baseline_`variable'' & "
	
	if `pval_model1_`variable'_aux'<0.05{
		file write Y2 "      & \textbf{`beta_model1_`variable''} & `pval_model1_`variable'' & "
	}
	else{
		file write Y2 "      & `beta_model1_`variable'' & `pval_model1_`variable'' & "
	}
	
	if `pval_model2_`variable'_aux'<0.05{
		file write Y2 "      & \textbf{`beta_model2_`variable''} & `pval_model2_`variable'' \\ " _n
	}
	else{
		file write Y2 "      & `beta_model2_`variable'' & `pval_model2_`variable'' \\ " _n
	}
}

file write Y2 "\hline"_n
file write Y2 "\end{tabular}"_n
file close Y2

**********************************************************
/*Table of Year 5 and 8*/

foreach year in 5 8{
	file open Y`year' using "$results/Y`year'_raw.tex", write replace
	file write Y`year' "\begin{tabular}{llccccccc}"_n
	file write Y`year' "\hline"_n
	file write Y`year' "\multirow{2}[2]{*}{\textbf{Measure}} &       & \multirow{2}[2]{*}{\textbf{Baseline}} &       & \multicolumn{2}{c}{\textbf{Model 1}} &       & \multicolumn{2}{c}{\textbf{Model 2}} \bigstrut[t]\\"_n
	file write Y`year' "      &       &       &       & \textbf{Estimate} & \textbf{p-value} &       & \textbf{Estimate} & \multicolumn{1}{c}{\textbf{p-value}} \bigstrut[b]\\"_n
	file write Y`year' "\cline{1-1}\cline{3-3}\cline{5-6}\cline{8-9}      &       &       &       &       &       &       &       &  \bigstrut[t]\\"_n

	forvalues x=1/5{/*5 blocks*/
		if `x'==1{
			file write Y`year' "\multicolumn{5}{l}{\textbf{Panel A. Woodcock-Johnson}} &       &       &       &  \\"_n
		}
		else if `x'==2{
			file write Y`year' "\multicolumn{5}{l}{\textbf{Panel B. SSRS Academic Subscale}} &       &       &       &  \\"_n
		}
		else if `x'==3{
			file write Y`year' "\multicolumn{5}{l}{\textbf{Panel C. Teachers' Mock Reports Cards}} &       &       &       &  \\"_n
		}
		else if `x'==4{
			file write Y`year' "\multicolumn{5}{l}{\textbf{Panel D. Classroom Behavior Scale}} &       &       &       &  \\"_n
		}
		else{
			file write Y`year' "\multicolumn{5}{l}{\textbf{Panel D. Parents' Reports}} &       &       &       &  \\"_n
		}

		foreach variable of varlist `Y`year'_B`x''{
			local lab: variable label `variable'
			file write Y`year' "`lab' (\$n=`n_`variable''\$) &       & `baseline_`variable'' & "
			if `pval_model1_`variable'_aux'<0.05{
				file write Y`year' "      & \textbf{`beta_model1_`variable''} & `pval_model1_`variable'' & "
			}
			else{
				file write Y`year' "      & `beta_model1_`variable'' & `pval_model1_`variable'' & "
			}
			
			if `pval_model2_`variable'_aux'<0.05{
				file write Y`year' "      & \textbf{`beta_model2_`variable''} & `pval_model2_`variable'' \\ " _n
			}
			else{
				file write Y`year' "      & `beta_model2_`variable'' & `pval_model2_`variable'' \\ " _n
			}


		}

	}



	file write Y`year' "\hline"_n
	file write Y`year' "\end{tabular}"_n
	file close Y`year'

}

*****************************************************************************************
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

		forvalues x=1/2{
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
reshape long model1_year model2_year sig_model1_year sig_model2_year, i(id) j(year)

forvalues x=1/2{
	twoway (scatter model`x' year, mlcolor(blue) mfcolor(none) msize(large)) /*
	*/ (scatter sig_model`x' year, mlcolor(blue) mfcolor(blue) msize(large)),/*
	*/ legend(off) ytitle("Impact on prob of being in the top 30%")  /*
	*/xtitle("Years after random assignment") /*
	*/ xlabel(2 5 8 , noticks) ylabel(, nogrid)/*
	*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white))/*
	*/ plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white)) scale(1.6)

	graph export "$results/ssrs_model`x'.pdf", as(pdf) replace

}

/*
*MOdel 1
twoway (hist year2_model1, fcolor(none) lcolor(black) ) /*
*/ (hist year5_model1, fcolor(none) lcolor(blue) ) /*
*/(hist year8_model1, fcolor(none) lcolor(red)),/*
*/ legend(order(1 "Year two" 2 "Year five" 3 "Year 8") region(lcolor(white)))/*
*/ytitle("Density")  xtitle("Impact on prob of being in the top 30%") /*
*/ xlabel( , noticks) ylabel(, nogrid)/*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white))/*
*/ plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))

graph export "$results/ssrs_model1.pdf", as(pdf) replace

*/



