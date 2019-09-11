/*
This do-file computes treatment effects on child outcomes using Fisher's exact 
p-values

*/


global databases "/home/jrodriguez/NH-secure"
global codes "/home/jrodriguez/NH_HC/codes"
global results "/home/jrodriguez/NH_HC/results/hh_summary"

clear
program drop _all
clear matrix
clear mata
set maxvar 15000
set more off
set matsize 2000

local reps = 2000


*******************************************************
/*Estimation sample: children of women*/
*******************************************************

use "$databases/Youth_original2.dta", clear

*labels
keep  sampleid child p_assign zboy agechild p_assign p_radaym sdkidbd



*Age at baseline
destring sdkidbd, force replace
format sdkidbd %td
gen year_birth=yofd(sdkidbd)

*child age at baseline
gen year_ra = substr(string(p_radaym),1,2)
destring year_ra, force replace
replace year_ra = 1900 + year_ra

gen age_t0=  year_ra - year_birth

*due to rounding errors, ages 0 and 11 are 1 and 10
replace age_t0=1 if age_t0==0
replace age_t0=10 if age_t0==11
drop if age_t0 < 1 | age_t0 > 11


keep age_t0 sampleid child p_assign sdkidbd
reshape wide age_t0 sdkidbd, i(sampleid) j(child)

tempfile child_aux
save `child_aux', replace


*Merge data with adults and drop those who do not merge
use "$databases/CFS_original.dta", clear
qui: do "$codes/data_cfs.do"

qui: count
local n_cfs = r(N)

merge 1:1 sampleid using `child_aux'
keep if _merge == 3
drop _merge

qui: count
local n_cfs2 = r(N)

keep if gender == 2

reshape long age_t0 sdkidbd, i(sampleid) j(child)

keep sampleid child
tempfile data_est
save `data_est'



/*ESTIMATES*/
use "$databases/Youth_original2.dta", clear


*labels
qui: do "$codes/data_youth.do"
keep  sampleid child p_assign zboy agechild p_assign p_radaym sdkidbd  /*
*/ tacad tq17* /* Y2: SSRS (block1)
*/ tcsbs tcsis tcsts tcstot  /* Y2: CBS (block2)
*/ t2q17a t2q17b t2q17c t2q17d t2q17e t2q17f t2q17g t2q17h t2q17i t2q17j /* Y5: SSRS (block2)
*/ etsq13a etsq13b etsq13c etsq13d etsq13e etsq13f etsq13g etsq13h etsq13i etsq13j /* Y8: teachers reports: SSRS academic subscale (block 2)
*/ piq146a piq146b piq146c piq146d /**/


*Age at baseline
destring sdkidbd, force replace
format sdkidbd %td
gen year_birth=yofd(sdkidbd)

*child age at baseline
gen year_ra = substr(string(p_radaym),1,2)
destring year_ra, force replace
replace year_ra = 1900 + year_ra

gen age_t0=  year_ra - year_birth

*due to rounding errors, ages 0 and 11 are 1 and 10
replace age_t0=1 if age_t0==0
replace age_t0=10 if age_t0==11
drop if age_t0 < 1 | age_t0 > 11


*gender
gen d_girl = 1 if zboy == "0"
replace d_girl= 0 if zboy == "1"



*Treatment
gen d_ra= 1 if p_assign == "E"
replace d_ra = 0 if p_assign == "C" 

/*Local labels: use these in regressions*/
local Y2_B1 tq17a tq17b tq17c tq17d tq17e tq17f tq17g tq17h tq17i tq17j
local Y5_B2 t2q17a t2q17b t2q17c t2q17d t2q17e t2q17f t2q17g t2q17h t2q17i t2q17j
local Y8_B2 etsq13a etsq13b etsq13c etsq13d etsq13e etsq13f etsq13g etsq13h etsq13i etsq13j
local Y2_B2 tcsbs tcsis tcsts

destring `Y2_B1' `Y5_B2' `Y8_B2' `Y2_B2' tacad tcstot , force replace



*Rounding up variables to the nearest integer
foreach variable of varlist `Y2_B1' `Y5_B2' `Y8_B2' {
	gen `variable'_s=round(`variable')
	drop `variable'
	rename `variable'_s `variable'
}


/*Computing SSRS scores*/
gen sample_2 = tq17a!=. & tq17b!=. & tq17c!=. & tq17d!=. & tq17e!=. & tq17f!=. & tq17g!=. & tq17h!=. & tq17i!=. & tq17j!=.
gen sample_5 = t2q17a!=. & t2q17b!=. & t2q17c!=. & t2q17d!=. & t2q17e!=. & t2q17f!=. & t2q17g!=. & t2q17h!=. & t2q17i!=. & t2q17j!=.
gen sample_8 = etsq13a!=. & etsq13b!=. & etsq13c!=. & etsq13d!=. & etsq13e!=. & etsq13f!=. & etsq13g!=. & etsq13h!=. & etsq13i!=. & etsq13j!=.


egen ssrs_2 = rowmean(`Y2_B1') 
egen ssrs_5 = rowmean(`Y5_B2') 
egen ssrs_8 = rowmean(`Y8_B2')

 *Rounding up variables to the nearest integer
foreach variable of varlist ssrs_2 ssrs_5 ssrs_8 {
	egen `variable'_s=std(`variable')
	drop `variable'
	rename `variable'_s `variable'
}


gen ra_girl	= d_ra*d_girl


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

label variable ssrs_2 "SSRS t=2"
label variable ssrs_5 "SSRS t=5"
label variable ssrs_8 "SSRS t=8"

merge 1:1 sampleid child using `data_est'
*This is the sample of children of women
keep if _merge == 3 | _merge == 2
drop _merge

******************************************************************************
/*ANALYSIS OF SUB-ITEMS*/
******************************************************************************


reg ssrs_2 d_ra
local beta_1 = _b[d_ra]
local lb_1 = _b[d_ra] - invttail(e(df_r),0.025)*_se[d_ra]
local ub_1 = _b[d_ra] + invttail(e(df_r),0.025)*_se[d_ra]

reg ssrs_2 d_ra if age_t0<=4
local beta_2 = _b[d_ra]
local lb_2 = _b[d_ra] - invttail(e(df_r),0.025)*_se[d_ra]
local ub_2 = _b[d_ra] + invttail(e(df_r),0.025)*_se[d_ra]


reg ssrs_2 d_ra if age_t0>4
local beta_3 = _b[d_ra]
local lb_3 = _b[d_ra] - invttail(e(df_r),0.025)*_se[d_ra]
local ub_3 = _b[d_ra] + invttail(e(df_r),0.025)*_se[d_ra]

/*graph*/
preserve	
clear
set obs 3
egen reg_type = seq()

gen lb = .
gen ub =.
gen beta = .

forvalues x =1/3{
	replace beta = `beta_`x'' if reg_type == `x'
	replace lb = `lb_`x'' if reg_type == `x'
	replace ub = `ub_`x'' if reg_type == `x'
}

graph twoway (scatter beta reg_type, mcolor(navy) msize(large)) ///
(rcap ub lb reg_type, lcolor(navy) lpattern(dash)), xlabel(0.5 " " 1 "All" 2 "Young" 3 "Old" 3.5 " ", noticks) ylabel(, nogrid) ///
 ytitle("Change in test score (in SD)")  xtitle("") yline(0,lstyle(foreground)) ///
 graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) ///
 plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white)) ///
 scale(1.1) legend(off) /*ylabel(0(.3)1.6) */

graph export "$results/childhc.pdf", as(pdf) replace

restore	

stop!!
foreach variable of varlist ssrs_2 ssrs_5 ssrs_8 {


	*Impacts

	qui xi: reg `variable' d_ra
	local beta_1_reg1_`variable' = string(round(_b[d_ra],0.001),"%9.3f")
	local n_1_reg1_`variable' = e(N)
	local r2_1_reg1_`variable' = string(round(e(r2),0.001),"%9.3f")

	qui xi: reg `variable' d_ra if age_t0<=4
	local beta_2_reg1_`variable' = string(round(_b[d_ra],0.001),"%9.3f")
	local n_2_reg1_`variable' = e(N)
	local r2_2_reg1_`variable' = string(round(e(r2),0.001),"%9.3f")

	qui xi: reg `variable' d_ra if age_t0>4
	local beta_3_reg1_`variable' = string(round(_b[d_ra],0.001),"%9.3f")
	local n_3_reg1_`variable' = e(N)
	local r2_3_reg1_`variable' = string(round(e(r2),0.001),"%9.3f")

	qui xi: reg `variable' d_ra c.d_ra#c.d_girl d_girl
	local beta_1_reg2_`variable' = string(round(_b[d_ra],0.001),"%9.3f")
	local int_1_reg2_`variable' = string(round(_b[c.d_ra#c.d_girl],0.001),"%9.3f")
	local n_1_reg2_`variable' = e(N)
	local r2_1_reg2_`variable' = string(round(e(r2),0.001),"%9.3f")
	
	qui xi: reg `variable' d_ra c.d_ra#c.d_girl d_girl if age_t0<=4
	local beta_2_reg2_`variable' = string(round(_b[d_ra],0.001),"%9.3f")
	local int_2_reg2_`variable' = string(round(_b[c.d_ra#c.d_girl],0.001),"%9.3f")
	local n_2_reg2_`variable' = e(N)
	local r2_2_reg2_`variable' = string(round(e(r2),0.001),"%9.3f")
	
	qui xi: reg `variable' d_ra c.d_ra#c.d_girl d_girl if age_t0>4
	local beta_3_reg2_`variable' = string(round(_b[d_ra],0.001),"%9.3f")
	local int_3_reg2_`variable' = string(round(_b[c.d_ra#c.d_girl],0.001),"%9.3f")
	local n_3_reg2_`variable' = e(N)
	local r2_3_reg2_`variable' = string(round(e(r2),0.001),"%9.3f")
	
	*pvalues

	qui: randcmd ((d_ra) reg `variable' d_ra), treatvars(d_ra) sample reps(`reps')
	mat mat_aux = e(REqn)
	local pvalue_aux = mat_aux[1,3]
	local pval_1_reg1_`variable' = string(round(`pvalue_aux',0.001),"%9.3f")

	qui: randcmd ((d_ra) reg `variable' d_ra if age_t0<=4), treatvars(d_ra) sample reps(`reps')
	mat mat_aux = e(REqn)
	local pvalue_aux = mat_aux[1,3]
	local pval_2_reg1_`variable' = string(round(`pvalue_aux',0.001),"%9.3f")

	qui: randcmd ((d_ra) reg `variable' d_ra if age_t0>4), treatvars(d_ra) sample reps(`reps')
	mat mat_aux = e(REqn)
	local pvalue_aux = mat_aux[1,3]
	local pval_3_reg1_`variable' = string(round(`pvalue_aux',0.001),"%9.3f")

	qui: randcmd ((d_ra ra_girl) reg `variable' d_ra d_girl	ra_girl), treatvars(d_ra) calc1(replace ra_girl	= d_ra*d_girl) sample reps(`reps')
	mat mat_aux = e(RCoef)
	local pvalue_aux = mat_aux[1,3]
	local pval_1_reg2_`variable' = string(round(`pvalue_aux',0.001),"%9.3f")
	local pvalue_aux = mat_aux[2,3]
	local pval_int_1_reg2_`variable' = string(round(`pvalue_aux',0.001),"%9.3f")

	qui: randcmd ((d_ra ra_girl) reg `variable' d_ra d_girl	ra_girl if age_t0<=4), treatvars(d_ra) calc1(replace ra_girl	= d_ra*d_girl) sample reps(`reps')
	mat mat_aux = e(RCoef)
	local pvalue_aux = mat_aux[1,3]
	local pval_2_reg2_`variable' = string(round(`pvalue_aux',0.001),"%9.3f")
	local pvalue_aux = mat_aux[2,3]
	local pval_int_2_reg2_`variable' = string(round(`pvalue_aux',0.001),"%9.3f")

	qui: randcmd ((d_ra ra_girl) reg `variable' d_ra d_girl	ra_girl if age_t0>4), treatvars(d_ra) calc1(replace ra_girl	= d_ra*d_girl) sample reps(`reps')
	mat mat_aux = e(RCoef)
	local pvalue_aux = mat_aux[1,3]
	local pval_3_reg2_`variable' = string(round(`pvalue_aux',0.001),"%9.3f")
	local pvalue_aux = mat_aux[2,3]
	local pval_int_3_reg2_`variable' = string(round(`pvalue_aux',0.001),"%9.3f")



}

/*Table*/

file open ssrs using "$results/ssrs_overall.tex", write replace
	file write ssrs "\begin{tabular}{lccccccccc}"_n
	file write ssrs "\hline"_n
	file write ssrs "      &       & \multicolumn{2}{c}{All} &       & \multicolumn{2}{c}{Age baseline$\leq4$} &       & \multicolumn{2}{c}{Age baseline$>4$} \bigstrut[t]\\"_n
	file write ssrs "      &       & (1)   & (2)   &       & (3)   & (4)   &       & (5)   & (6) \bigstrut[b]\\"_n
	file write ssrs "\hline"_n
	file write ssrs "&       &       &       &       &       &       &       &       &  \bigstrut[t]\\"_n
	file write ssrs "A. Two years after baseline &       &       &       &       &       &       &       &       &  \\"_n
	file write ssrs "Treatment &       & `beta_1_reg1_ssrs_2'  &    `beta_1_reg2_ssrs_2'    &       &   `beta_2_reg1_ssrs_2'     &   `beta_2_reg2_ssrs_2'     &       &   `beta_3_reg1_ssrs_2'     & `beta_3_reg2_ssrs_2'  \\"_n
	file write ssrs " &       & [`pval_1_reg1_ssrs_2']  &    [`pval_1_reg2_ssrs_2']    &       &   [`pval_2_reg1_ssrs_2']     &   [`pval_2_reg2_ssrs_2']     &       &   [`pval_3_reg1_ssrs_2']     & [`pval_3_reg2_ssrs_2']  \\"_n
	file write ssrs "Treatment\$\times\$Girl &       &   &    `int_1_reg2_ssrs_2'    &       &        &   `int_2_reg2_ssrs_2'     &       &       & `int_3_reg2_ssrs_2'  \\"_n
	file write ssrs " &       &   &    [`pval_int_1_reg2_ssrs_2']    &       &       &   [`pval_int_2_reg2_ssrs_2']     &       &       & [`pval_int_3_reg2_ssrs_2']  \\"_n
	file write ssrs "&       &       &       &       &       &       &       &       &  \bigstrut[t]\\"_n
	file write ssrs "Observations &       & `n_1_reg1_ssrs_2'  &    `n_1_reg2_ssrs_2'    &       &   `n_2_reg1_ssrs_2'     &   `n_2_reg2_ssrs_2'     &       &   `n_3_reg1_ssrs_2'     & `n_3_reg2_ssrs_2'  \\"_n
	file write ssrs "\$R^2\$ &       & `r2_1_reg1_ssrs_2'  &    `r2_1_reg2_ssrs_2'    &       &   `r2_2_reg1_ssrs_2'     &   `r2_2_reg2_ssrs_2'     &       &   `r2_3_reg1_ssrs_2'     & `r2_3_reg2_ssrs_2'  \\"_n
	file write ssrs "&       &       &       &       &       &       &       &       &  \bigstrut[t]\\"_n
	file write ssrs "B. Five years after baseline &       &       &       &       &       &       &       &       &  \\"_n
	file write ssrs "Treatment &       & `beta_1_reg1_ssrs_5'  &    `beta_1_reg2_ssrs_5'    &       &   `beta_2_reg1_ssrs_5'     &   `beta_2_reg2_ssrs_5'     &       &   `beta_3_reg1_ssrs_5'     & `beta_3_reg2_ssrs_5'  \\"_n
	file write ssrs " &       & [`pval_1_reg1_ssrs_5']  &    [`pval_1_reg2_ssrs_5']    &       &   [`pval_2_reg1_ssrs_5']     &   [`pval_2_reg2_ssrs_5']     &       &   [`pval_3_reg1_ssrs_5']     & [`pval_3_reg2_ssrs_5']  \\"_n
	file write ssrs "Treatment\$\times\$Girl &       &   &    `int_1_reg2_ssrs_5'    &       &        &   `int_2_reg2_ssrs_5'     &       &       & `int_3_reg2_ssrs_5'  \\"_n
	file write ssrs " &       &   &    [`pval_int_1_reg2_ssrs_5']    &       &       &   [`pval_int_2_reg2_ssrs_5']     &       &       & [`pval_int_3_reg2_ssrs_5']  \\"_n
	file write ssrs "&       &       &       &       &       &       &       &       &  \bigstrut[t]\\"_n
	file write ssrs "Observations &       & `n_1_reg1_ssrs_5'  &    `n_1_reg2_ssrs_5'    &       &   `n_2_reg1_ssrs_5'     &   `n_2_reg2_ssrs_5'     &       &   `n_3_reg1_ssrs_5'     & `n_3_reg2_ssrs_5'  \\"_n
	file write ssrs "\$R^2\$ &       & `r2_1_reg1_ssrs_5'  &    `r2_1_reg2_ssrs_5'    &       &   `r2_2_reg1_ssrs_5'     &   `r2_2_reg2_ssrs_5'     &       &   `r2_3_reg1_ssrs_5'     & `r2_3_reg2_ssrs_5'  \\"_n
	file write ssrs "&       &       &       &       &       &       &       &       &  \bigstrut[t]\\"_n
	file write ssrs "C. Eight years after baseline &       &       &       &       &       &       &       &       &  \\"_n
	file write ssrs "Treatment &       & `beta_1_reg1_ssrs_8'  &    `beta_1_reg2_ssrs_8'    &       &   `beta_2_reg1_ssrs_8'     &   `beta_2_reg2_ssrs_8'     &       &   `beta_3_reg1_ssrs_8'     & `beta_3_reg2_ssrs_8'  \\"_n
	file write ssrs " &       & [`pval_1_reg1_ssrs_8']  &    [`pval_1_reg2_ssrs_8']    &       &   [`pval_2_reg1_ssrs_8']     &   [`pval_2_reg2_ssrs_8']     &       &   [`pval_3_reg1_ssrs_8']     & [`pval_3_reg2_ssrs_8']  \\"_n
	file write ssrs "Treatment\$\times\$Girl &       &   &    `int_1_reg2_ssrs_8'    &       &        &   `int_2_reg2_ssrs_8'     &       &       & `int_3_reg2_ssrs_8'  \\"_n
	file write ssrs " &       &   &    [`pval_int_1_reg2_ssrs_8']    &       &       &   [`pval_int_2_reg2_ssrs_8']     &       &       & [`pval_int_3_reg2_ssrs_8']  \\"_n
	file write ssrs "&       &       &       &       &       &       &       &       &  \bigstrut[t]\\"_n
	file write ssrs "Observations &       & `n_1_reg1_ssrs_8'  &    `n_1_reg2_ssrs_8'    &       &   `n_2_reg1_ssrs_8'     &   `n_2_reg2_ssrs_8'     &       &   `n_3_reg1_ssrs_8'     & `n_3_reg2_ssrs_8'  \\"_n
	file write ssrs "\$R^2\$ &       & `r2_1_reg1_ssrs_8'  &    `r2_1_reg2_ssrs_8'    &       &   `r2_2_reg1_ssrs_8'     &   `r2_2_reg2_ssrs_8'     &       &   `r2_3_reg1_ssrs_8'     & `r2_3_reg2_ssrs_8'  \\"_n
	file write ssrs "\hline"_n
	file write ssrs "\end{tabular}"_n
	file close ssrs

stop!



/*
******************************************************************************
/*ANALYSIS OF SUB-ITEMS*/
******************************************************************************


foreach variable of varlist `Y2_B1' `Y5_B2' `Y8_B2' {

	qui: count if `variable'!=. & age_t0<=4
	local n_`variable'=r(N)

	qui: gen d_base = `variable' >= 4
	qui: sum d_base if `variable'!=.
	local baseline_`variable' = string(round(r(mean),0.001),"%9.3f")
	drop d_base
	
	*original estimates and MFx
	qui: oprobit `variable' d_ra if age_t0<=4
	qui: test d_ra
	local pvalue_`variable' = r(p)
	local pvalue_short_`variable' = string(round(`pvalue_`variable'',0.001),"%9.3f")
	qui: predict xbetas, xb
	gen xbetas_tilde = xbetas - _b[d_ra]*d_ra
	gen pr_1 = 1-normal(_b[/cut3]- (xbetas_tilde + _b[d_ra]))
	gen pr_0 = 1-normal(_b[/cut3]- (xbetas_tilde))
	gen dpr = pr_1 - pr_0
	qui: sum dpr
	local beta_model1_orig_`variable'= r(mean)
	local beta_model1_`variable' = string(round(r(mean),0.001),"%9.3f")
	drop xbetas* pr_0 pr_1 dpr

	*fisher's exact pvalues
	qui: randcmd ((d_ra) oprobit `variable' d_ra if age_t0<=4), treatvars(d_ra) sample
	mat mat_aux = e(REqn)
	local pvalue2_`variable' = mat_aux[1,3]
	local pvalue2_short_`variable' = string(round(`pvalue2_`variable'',0.001),"%9.3f")



}



/*Table*/


file open Y2 using "$results/ssrs_summary.tex", write replace
	file write Y2 "\begin{tabular}{lcccccccc}"_n
	file write Y2 "\hline"_n
	file write Y2 "\multicolumn{1}{c}{\multirow{2}[2]{*}{Measure}} &       & \multicolumn{1}{c}{\multirow{2}[2]{*}{Baseline}} &       & \multirow{2}[2]{*}{Effect size} &       & \multicolumn{3}{c}{p-values} \bigstrut[t]\\"_n
	file write Y2 "      &       &       &       &       &       & Standard &       & Exact \bigstrut[b]\\"_n
	file write Y2 "\hline"_n
	file write Y2 "         &       &       &       &       &       &       &       &  \bigstrut[t]\\"_n
	file write Y2 "A. Two years after baseline &       &       &       &       &       &       &       &  \\"_n

	foreach variable in `Y2_B1'{
		local labs: variable label `variable'
		file write Y2 "   `labs' (\$n=`n_`variable''\$)      &       &     `baseline_`variable''   &       &    `beta_model1_`variable''   &       &    `pvalue_short_`variable''   &       & `pvalue2_short_`variable'' \bigstrut[t]\\"_n
	}
	file write Y2 "         &       &       &       &       &       &       &       &  \bigstrut[t]\\"_n

	file write Y2 "B. Five years after baseline &       &       &       &       &       &       &       &  \\"_n

	foreach variable in `Y5_B2'{
		local labs: variable label `variable'
		file write Y2 "   `labs' (\$n=`n_`variable''\$)      &       &     `baseline_`variable''   &       &    `beta_model1_`variable''   &       &    `pvalue_short_`variable''   &       & `pvalue2_short_`variable'' \bigstrut[t]\\"_n
	}

	file write Y2 "         &       &       &       &       &       &       &       &  \bigstrut[t]\\"_n
	file write Y2 "C. Eight years after baseline &       &       &       &       &       &       &       &  \\"_n

	foreach variable in `Y8_B2'{
		local labs: variable label `variable'
		file write Y2 "   `labs' (\$n=`n_`variable''\$)      &       &     `baseline_`variable''   &       &    `beta_model1_`variable''   &       &    `pvalue_short_`variable''   &       & `pvalue2_short_`variable'' \bigstrut[t]\\"_n
	}

	file write Y2 "\hline"_n
	file write Y2 "\end{tabular}"_n
	file close Y2


/*Graph: SSRS*/
preserve
clear
set obs 10

foreach year in 2 5 8{
	gen effect_year`year'=.
	gen sig_year`year'=.	
}

local i = 1
foreach variable in `Y2_B1' {
	if `pvalue_`variable''>0.05{
		replace effect_year2 = `beta_model1_orig_`variable'' if _n == `i'
	}
	else{
		replace sig_year2 = `beta_model1_orig_`variable'' if _n == `i'
	}
	local i = `i' + 1
}

local i = 1
foreach variable in `Y5_B2' {
	if `pvalue_`variable''>0.05{
		replace effect_year5 = `beta_model1_orig_`variable'' if _n == `i'
	}
	else{
		replace sig_year5 = `beta_model1_orig_`variable'' if _n == `i'
	}
	local i = `i' + 1
}

local i = 1
foreach variable in `Y8_B2' {
	if `pvalue_`variable''>0.05{
		replace effect_year8 = `beta_model1_orig_`variable'' if _n == `i'
	}
	else{
		replace sig_year8 = `beta_model1_orig_`variable'' if _n == `i'
	}
	local i = `i' + 1
}

egen id = seq()
reshape long effect_year sig_year, i(id) j(year)

twoway (scatter effect_year year, mlcolor(blue) mfcolor(none) msize(large)) (scatter sig_year year, mlcolor(blue) mfcolor(blue) msize(large)), legend(off) ytitle("Impact on Pr(top 30%)")  xtitle("Years after random assignment") xlabel(2 5 8 , noticks) ylabel(, nogrid) graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white)) scale(1.4)

restore


graph export "$results/ssrs_summary.pdf", as(pdf) replace

*/
