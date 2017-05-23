/*

This do-file computes the impact of NH on total income.
Income is measured using administrative sources.

Income sources:
-UI
-Earnings supplement
-CSJs
-EITC


To compute effects by employment status: change local 'emp"

*/

global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"


local SE="hc2"

clear
clear matrix
clear mata
set more off
set maxvar 15000

/*
controls: choose if regression should include controls for parents: age, ethnicity, marital status, and education.
*/

local controls=1

*Choose: 1 if produce income graph for employed at baseline
*Choose: 0 if produce income graph for unemployed at baseline
*Choose: 3 if total
local emp=3

use "$results/Income/data_income.dta", clear

drop total_income_y0 gross_y0 gross_nominal_y0 grossv2_y0 employment_y0 /*
*/ fs_y0 afdc_y0 sup_y0 eitc_state_y0 eitc_fed_y0
forvalues x=1/9{
	local z=`x'-1
	rename total_income_y`x' total_income_y`z'
	rename gross_y`x' gross_y`z'
	rename grossv2_y`x' grossv2_y`z'
	rename gross_nominal_y`x' gross_nominal_y`z'
	rename employment_y`x' employment_y`z'
	rename afdc_y`x' afdc_y`z'
	rename fs_y`x' fs_y`z'
	rename sup_y`x' sup_y`z'
	rename eitc_fed_y`x' eitc_fed_y`z'
	rename eitc_state_y`x' eitc_state_y`z'

}



*Many missing obs
drop total_income_y10


*****************************************
*****************************************
*THE FIGURES
*****************************************
*****************************************

*Dropping 50 adults with no information on their children
count
qui: do "$codes/income/drop_50.do"
count

*Control variables (and recovering p_assign)
qui: do "$codes/income/Xs.do"
if `controls'==1{

	
	local control_var age_ra i.marital i.ethnic d_HS2 higrade i.pastern2
}

*Sample
if `emp'==1{
	keep if emp_baseline==1
}
else if `emp'==0{
	keep if emp_baseline==0

}

*dummy RA for ivqte
gen d_ra = .
replace d_ra = 1 if p_assign=="E"
replace d_ra = 0 if p_assign=="C"

*Save temporal data (before panel)
tempfile data_aux
save `data_aux', replace


*To panel
keep total_income_y* gross_y* employment_y* afdc_y* fs_y* sup_y* eitc_fed_y* /*
*/ eitc_state_y* sampleid d_ra p_assign emp_baseline age_ra marital ethnic d_HS2 higrade pastern2

reshape long total_income_y gross_y employment_y afdc_y fs_y eitc_fed_y sup_y  /*
*/ eitc_state_y, i(sampleid) j(year)

drop if year>8

*Save panel data
tempfile data_panel
save `data_panel', replace


*Welfare
egen welfare=rowtotal(afdc_y fs_y)

egen eitc=rowtotal(eitc_fed_y eitc_state_y)


**********************************************************************************
**********************************************************************************
/*TOTAL INCOME ESTIMATES*/


*The regressions
forvalues t=0/1{/*the periods loop*/
	preserve

	if `t'==1{
		keep if year<=2	

	}
	forvalues j=0/1{/*the control var loop*/

		if `j'==0{
			local controls ""
		}
		else{
			local controls `control_var'
		}
		forvalues x=0/2{/*the sample loop*/
			if `x'<=1{
				qui xi: reg total_income_y i.p_assign `controls' if emp_baseline==`x', vce(`SE')	
			}
			else{
				qui xi: reg total_income_y i.p_assign `controls', vce(`SE')		
			}
			
			local total_emp`x'_control`j'_period`t' = string(round(_b[_Ip_assign_2]/1000,0.001),"%9.3f")
			local se_total_emp`x'_control`j'_period`t'  =string(round(_se[_Ip_assign_2]/1000,0.001),"%9.3f")
			qui: test _Ip_assign_2=0
			local pv_total_emp`x'_control`j'_period`t'=r(p)

			if `pv_total_emp`x'_control`j'_period`t''<=.01{
				local ast_total_emp`x'_control`j'_period`t' ="***"	
			}
			else if `pv_total_emp`x'_control`j'_period`t''<=.05 {
				local ast_total_emp`x'_control`j'_period`t' ="**"		
			}
			else if `pv_total_emp`x'_control`j'_period`t''<=.1 {
				local ast_total_emp`x'_control`j'_period`t' ="*"		
			}
			else{
				local ast_total_emp`x'_control`j'_period`t'=""
			}
			




		}

	}
	restore

}



*The Table
file open tab_income using "$results/Income/table_total_income.tex", write replace
file write tab_income
file write tab_income "\begin{tabular}{llccccccc}" _n
file write tab_income "\hline" _n
file write tab_income "Sample & & (1)   && (2) & & (3)   & & (4) \bigstrut\\" _n
file write tab_income "\cline{1-1}\cline{3-3}\cline{5-5}\cline{7-7}\cline{9-9}"_n

file write tab_income "Overall &   & `total_emp2_control0_period0'`ast_total_emp2_control0_period0'   &  & `total_emp2_control0_period1'`ast_total_emp2_control0_period1'  &  & `total_emp2_control1_period0'`ast_total_emp2_control1_period0'   &  & `total_emp2_control1_period1'`ast_total_emp2_control1_period1' \bigstrut[t]\\" _n
file write tab_income " &   & (`se_total_emp2_control0_period0')   &  & (`se_total_emp2_control0_period1')  &  & (`se_total_emp2_control1_period0')   &  & (`se_total_emp2_control0_period1') \bigstrut[t]\\" _n

file write tab_income "Unemployed at baseline &   & `total_emp0_control0_period0'`ast_total_emp0_control0_period0'   &  & `total_emp0_control0_period1'`ast_total_emp0_control0_period1'  &  & `total_emp0_control1_period0'`ast_total_emp0_control1_period0'   &  & `total_emp0_control1_period1'`ast_total_emp0_control1_period1' \bigstrut[t]\\" _n
file write tab_income " &   & (`se_total_emp0_control0_period0')   &  & (`se_total_emp0_control0_period1')  &  & (`se_total_emp0_control1_period0')   &  & (`se_total_emp0_control0_period1') \bigstrut[t]\\" _n

file write tab_income "Employed at baseline &   & `total_emp1_control0_period0'`ast_total_emp1_control0_period0'   &  & `total_emp1_control0_period1'`ast_total_emp1_control0_period1'  &  & `total_emp1_control1_period0'`ast_total_emp1_control1_period0'   &  & `total_emp1_control1_period1'`ast_total_emp1_control1_period1' \bigstrut[t]\\" _n
file write tab_income " &   & (`se_total_emp1_control0_period0')   &  & (`se_total_emp1_control0_period1')  &  & (`se_total_emp1_control1_period0')   &  & (`se_total_emp1_control0_period1') \bigstrut[t]\\" _n


file write tab_income "\hline" _n
file write tab_income "All years &       & $\checkmark$ &       &       &       & $\checkmark$ &       &  \bigstrut[t]\\" _n
file write tab_income "Years 0-2 &       &       &       & $\checkmark$ &       &       &       & $\checkmark$ \\" _n
file write tab_income "No controls &       & $\checkmark$ &       & $\checkmark$ &       &       &       &  \\" _n
file write tab_income "W/ controls &       &       &       &       &       & $\checkmark$ &       & $\checkmark$ \bigstrut[b]\\" _n
file write tab_income "\hline" _n
file write tab_income "\end{tabular}" _n
file close tab_income

*************************************************************************************
*************************************************************************************
*************************************************************************************
/*CONTRIBUTION OF EARNINGS/WELFARE/NH/EITC*/



************************************************************************************
*

*For t<=2
forvalues x=0/2{

	if `x'<=1{
		qui xi: reg gross_y i.p_assign if emp_baseline==`x' & year<=2, vce(`SE')
		local dec1_emp`x' = _b[_Ip_assign_2]

		qui xi: reg welfare i.p_assign if emp_baseline==`x' & year<=2, vce(`SE')
		local dec2_emp`x' = _b[_Ip_assign_2]

		qui xi: reg eitc i.p_assign if emp_baseline==`x' & year<=2, vce(`SE')
		local dec3_emp`x' = _b[_Ip_assign_2]

		qui xi: reg sup_y i.p_assign if emp_baseline==`x' & year<=2, vce(`SE')
		local dec4_emp`x' = _b[_Ip_assign_2]

		*shares
		qui xi: reg total_income_y i.p_assign if emp_baseline==`x' & year<=2, vce(`SE')
		local tot = _b[_Ip_assign_2]

		forvalues j=1/4{
			local share_dec`j'_emp`x' = string(round((`dec`j'_emp`x''/`tot')*100,0.01),"%9.2f")
			local dec`j'_emp`x'=string(round(`dec`j'_emp`x''/1000,0.001),"%9.3f")/*rounding*/
		}
		


	}
	else{
		qui xi: reg gross_y i.p_assign if year<=2, vce(`SE')
		local dec1_emp`x' = _b[_Ip_assign_2]

		qui xi: reg welfare i.p_assign if year<=2, vce(`SE')
		local dec2_emp`x' = _b[_Ip_assign_2]

		qui xi: reg eitc i.p_assign if year<=2, vce(`SE')
		local dec3_emp`x' = _b[_Ip_assign_2]

		qui xi: reg sup_y i.p_assign if year<=2, vce(`SE')
		local dec4_emp`x' = _b[_Ip_assign_2]

		*shares
		qui xi: reg total_income_y i.p_assign if year<=2, vce(`SE')
		local tot = _b[_Ip_assign_2]

		forvalues j=1/4{
			local share_dec`j'_emp`x' = string(round((`dec`j'_emp`x''/`tot')*100,0.01),"%9.2f")
			local dec`j'_emp`x'=string(round(`dec`j'_emp`x''/1000,0.001),"%9.3f")/*rounding*/
		}
		
	}
		
	
}

file open tab_dec using "$results/Income/table_income_decomposition.tex", write replace
file write tab_dec
file write tab_dec "\begin{tabular}{llccccc}"_n
file write tab_dec "\hline"_n
file write tab_dec "      &       & (1)   &       & (2)   &       & (3) \bigstrut\\"_n
file write tab_dec "   \cline{1-1}\cline{3-3}\cline{5-5}\cline{7-7}"_n
*the estimates here

local x=1
foreach name in "Earnings" "Welfare" "EITC" "New Hope"{
	file write tab_dec " `name' && `dec`x'_emp2'  && `dec`x'_emp0'  && `dec`x'_emp1' \bigstrut[t]\\"_n	
	file write tab_dec "  && [`share_dec`x'_emp2'\%]  && [`share_dec`x'_emp0'\%]  && [`share_dec`x'_emp1'\%] \bigstrut[t]\\"_n
	local x=`x'+1
}

file write tab_dec " Total &&  `total_emp2_control0_period1' && `total_emp0_control0_period1'  && `total_emp1_control0_period1' \bigstrut[t]\\"_n
file write tab_dec "  &&  [100\%] && [100\%]  && [100\%] \bigstrut[t]\\"_n

file write tab_dec "\hline"_n
file write tab_dec "Overall & & $\checkmark$      &&        &&   \bigstrut[t]\\"_n
file write tab_dec "Unemployed at baseline &&       && $\checkmark$      &&  \bigstrut[t]\\"_n
file write tab_dec "Employed at baseline &&       &&       && $\checkmark$  \bigstrut[t]\\"_n
file write tab_dec "\hline"_n
file write tab_dec "\end{tabular}"_n
file close tab_dec



***************************************************************************************************
***************************************************************************************************
/*QTE*/


qui: ivqte gross_y (d_ra) if year<=2, /*
*/quantiles(.5 .1 .15 .2 .25 .3 .35 .4 .45 .5 /*
*/ .55 .60 .65 .7 .75 .8 .85 .90 .95) variance
	forvalues q=1/19{
		local mean_q`q' = _b[Quantile_`q']
		local lb_q`q'=_b[Quantile_`q'] - invnormal(0.975)*_se[Quantile_`q']
		local ub_q`q'=_b[Quantile_`q'] + invnormal(0.975)*_se[Quantile_`q']
		qui: test Quantile_`q'=0
		local pvalue_q`q'=r(p)

	}


/*The QTE figure*/
preserve

clear
set obs 19
gen quan=.
gen effect=.
gen lb=.
gen ub=.
gen pvalues=.


local obs=1
forvalues q=1/19{
	replace effect=`mean_q`q'' if _n==`obs'
	replace lb=`lb_q`q'' if _n==`obs'
	replace ub=`ub_q`q'' if _n==`obs'
	replace pvalues=`pvalue_q`q'' if _n==`obs'

	replace quan=`q' if _n==`obs'
	local obs=`obs'+1
	
	
}

gen mean_aux_1=effect if pvalues<0.05


twoway (connected effect quan,msymbol(circle) mlcolor(blue) mfcolor(white))/*
*/ (scatter mean_aux_1 quan, msymbol(circle) mlcolor(blue) mfcolor(blue)) /* 
*/ (line ub  quan, lpattern(dash)) /*
*/ (line lb quan, lpattern(dash)), /*
*/ ytitle("Effect on earnings (2003 dollars)")  xtitle("Quantile") legend(off) /*
*/ xlabel( 2 "10" 4 "20" 6 "30" 8 "40" 10 "50" 12 "60" 14 "70" 16 "80" 18 "90", noticks) /*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) /*
*/plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid) yline(0, lpattern(solid) lcolor(black)) scale(1.2) 


graph export "$results/Income/earnings_QTE.pdf", as(pdf) replace


restore




**********************************
/*Diff-in-Diff analysis*/
**********************************
use `data_aux', clear
keep sampleid total_income_y* p_assign age_ra marital ethnic d_HS2 higrade pastern2

*the panel
reshape long total_income_y, i(sampleid) j(year)

*Back to the original timing
replace year=year-1

*Diff-in-diff loop
gen d_after=year>=0
gen d_ra=p_assign=="E"
gen d_ate=d_after*d_ra



forvalues y=0/8{
	qui: reg total_income_y d_ra d_after d_ate `control_var' if year==-1 | year==`y', vce(`SE')
	test d_ate=0
	
	if `y'==0{
		mat pvalue=r(p)
	}
	
	else{
		mat pvalue=pvalue\r(p)
	}
	local mean_`y'=_b[d_ate]
	local lb_`y'=_b[d_ate] - invttail(e(df_r),0.025)*_se[d_ate]
	local ub_`y'=_b[d_ate] + invttail(e(df_r),0.025)*_se[d_ate]
	
	}

*The graph
clear
set obs 9 /*6 years*/
gen year=.
gen effect=.
gen lb=.
gen ub=.
gen pvalues=.

local obs=1
forvalues year=0/8{
	replace effect=`mean_`year'' if _n==`obs'
	replace lb=`lb_`year'' if _n==`obs'
	replace ub=`ub_`year'' if _n==`obs'
	replace pvalues=pvalue[`obs',1] if _n==`obs'
	replace year=`year' if _n==`obs'
	local obs=`obs'+1
	
	
}

*To indicate p-value in graph
gen mean_aux_1=effect if pvalues<0.05
gen mean_aux_2=effect if pvalues>=0.05

*new identifier
gen year2=year*2

twoway (bar effect year2) (rcap ub lb year2) /* These are the mean effect and the 90% confidence interval
*/ (scatter mean_aux_1 year2,  msymbol(circle) mcolor(blue) mfcolor(blue)) (scatter mean_aux_2 year2,   msymbol(circle) mcolor(blue) mfcolor(none)), /*
*/ ytitle("Annual income (2003 dollars)")  xtitle("Years after random assignment") legend(off) /*
*/ xlabel( 0 "0" 2 "1" 4 "2" 6 "3" 8 "4" 10 "5" 12 "6" 14 "7" 16 "8", noticks) /*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid) yline(0, lpattern(solid) lcolor(black))

graph export "$results/Income/income_diffdiff.pdf", as(pdf) replace








