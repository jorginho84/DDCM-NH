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


forvalues y=0/8{

	qui xi: reg total_income_y`y' i.p_assign `control_var', vce(`SE')
	local mean_`y' = _b[_Ip_assign_2]
	local lb_`y'=_b[_Ip_assign_2] - invttail(e(df_r),0.025)*_se[_Ip_assign_2]
	local ub_`y'=_b[_Ip_assign_2] + invttail(e(df_r),0.025)*_se[_Ip_assign_2]
	qui: test _Ip_assign_2=0
	local pvalue_`y'=r(p)

	qui xi: reg gross_y`y' i.p_assign `control_var', vce(`SE')
	local mean_gross_`y' = _b[_Ip_assign_2]
	local lb_gross_`y'=_b[_Ip_assign_2] - invttail(e(df_r),0.025)*_se[_Ip_assign_2]
	local ub_gross_`y'=_b[_Ip_assign_2] + invttail(e(df_r),0.025)*_se[_Ip_assign_2]
	qui: test _Ip_assign_2=0
	local pvalue_gross_`y'=r(p)

	



}

egen gross_nh_period = rowmean(gross_y0 gross_y1 gross_y2)

qui: ivqte gross_nh_period (d_ra), quantiles(.5 .1 .15 .2 .25 .3 .35 .4 .45 .5 /*
*/ .55 .60 .65 .7 .75 .8 .85 .90 .95) variance
	forvalues q=1/19{
		local mean_q`q' = _b[Quantile_`q']
		local lb_q`q'=_b[Quantile_`q'] - invnormal(0.975)*_se[Quantile_`q']
		local ub_q`q'=_b[Quantile_`q'] + invnormal(0.975)*_se[Quantile_`q']
		qui: test Quantile_`q'=0
		local pvalue_q`q'=r(p)

	}

*********************
/*The figure*/
*********************
preserve

clear
set obs 10
gen year=.
gen effect=.
gen lb=.
gen ub=.
gen pvalues=.
gen effect_gross=.
gen lb_gross=.
gen ub_gross=.
gen pvalues_gross=.



local obs=1
forvalues year=0/8{
	replace effect=`mean_`year'' if _n==`obs'
	replace lb=`lb_`year'' if _n==`obs'
	replace ub=`ub_`year'' if _n==`obs'
	replace pvalues=`pvalue_`year'' if _n==`obs'

	replace effect_gross=`mean_gross_`year'' if _n==`obs'
	replace lb_gross=`lb_gross_`year'' if _n==`obs'
	replace ub_gross=`ub_gross_`year'' if _n==`obs'
	replace pvalues_gross=`pvalue_gross_`year'' if _n==`obs'
	

	
	replace year=`year' - 1 if _n==`obs' /*original timing*/
	local obs=`obs'+1
	
	
}

gen mean_aux_1=effect if pvalues<0.05
gen mean_gross_aux_1=effect_gross if pvalues_gross<0.05


gen year2=year*2

twoway (connected effect year2,msymbol(circle) mlcolor(blue) mfcolor(white))/*
*/ (scatter mean_aux_1 year2, msymbol(circle) mlcolor(blue) mfcolor(blue)) /* 
*/ (line ub  year2, lpattern(dash)) /*
*/ (line lb year2, lpattern(dash)), /*
*/ ytitle("Change in annual income (2003 dollars)")  xtitle("Years after random assignment") legend(off) /*
*/ xlabel( -2 "-1" 0 "0" 2 "1" 4 "2" 6 "3" 8 "4" 10 "5" 12 "6" 14 "7" 16 "8", noticks) /*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) /*
*/plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid) yline(0, lpattern(solid) lcolor(black)) scale(1.2) /*
*/ xline(5, lcolor(red))

graph export "$results/Income/total_income_annual_controls`controls'_emp`emp'.pdf", as(pdf) replace

twoway (connected effect_gross year2,msymbol(circle) mlcolor(blue) mfcolor(white))/*
*/ (scatter mean_gross_aux_1 year2, msymbol(circle) mlcolor(blue) mfcolor(blue)) /* 
*/ (line ub_gross  year2, lpattern(dash)) /*
*/ (line lb_gross year2, lpattern(dash)) ,/*
*/ ytitle("Change in earnings (2003 dollars)")  xtitle("Years after random assignment") legend(off) /*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) /*
*/plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid) yline(0, lpattern(solid) lcolor(black)) scale(1.2) /*
*/ xline(5, lcolor(red))

graph export "$results/Income/earnings_annual_controls`controls'_emp`emp'.pdf", as(pdf) replace



restore

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
*/ ytitle("Change in earnings (2003 dollars)")  xtitle("Quantile") legend(off) /*
*/ xlabel( 2 "10" 4 "20" 6 "30" 8 "40" 10 "50" 12 "60" 14 "70" 16 "80" 18 "90", noticks) /*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) /*
*/plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid) yline(0, lpattern(solid) lcolor(black)) scale(1.2) 


graph export "$results/Income/earnings_QTE.pdf", as(pdf) replace


restore

/*These numbers go in the text*/
/*
forvalues x=1/3{
	qui xi: reg total_income_y`x' i.p_assign `control_var', vce(`SE')
	local beta_year`x'=_b[_Ip_assign_2]
	display `beta_year`x''
	qui: sum total_income_y`x' if p_assign=="C"
	local m_`y'_control=r(mean)
	display `m_`y'_control'
	
}
*/

egen total_income_raperiod=rowmean(total_income_y1 total_income_y2 total_income_y3)
xi: reg total_income_raperiod i.p_assign age_ra i.marital i.ethnic d_HS2 higrade i.pastern2, vce(`SE')
sum total_income_raperiod if p_assign=="C"


xi: reg total_income_y2 i.p_assign age_ra i.marital i.ethnic d_HS2 higrade i.pastern2, vce(`SE')
sum total_income_y2 if p_assign=="C"


**********************************
/*Diff-in-Diff analysis*/
**********************************
preserve
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





restore


**********************************
/*Decomposition*/
**********************************

*Welfare payments
forvalues y=0/8{
	egen wel_y`y' = rowtotal(afdc_y`y' fs_y`y' eitc_fed_y`y' eitc_state_y`y')
}

*Earnings: gross_y

*New Hope supplement: supy0-supy2

forvalues y=3/8{
	replace sup_y`y'=0
}

*Total
forvalues y=0/8{
	egen income_y`y' = rowtotal(gross_y`y' sup_y`y' wel_y`y')
}



forvalues y=0/8{
	xi: reg gross_y`y' i.p_assign
	local effect_gross_y`y' = _b[_Ip_assign_2]

	xi: reg sup_y`y' i.p_assign
	local effect_sup_y`y' = _b[_Ip_assign_2]

	xi: reg wel_y`y' i.p_assign
	local effect_wel_y`y' = _b[_Ip_assign_2]

	xi: reg income_y`y' i.p_assign
	local effect_total_y`y' = _b[_Ip_assign_2]

}

*Graph: area

clear
set obs 9
gen year=.
gen effect_gross=.
gen effect_wel=.
gen effect_sup=.
gen effect=.

forvalues y=0/8{
	replace effect_gross = `effect_gross_y`y'' if _n==`y'+1
	replace effect_wel = `effect_wel_y`y'' if _n==`y'+1
	replace effect_sup = `effect_sup_y`y'' if _n==`y'+1
	replace effect = `effect_total_y`y'' if _n==`y'+1
	replace year = `y' if _n==`y'+1
}

*Cumultivate effect: baseline is "wel"
gen effect_wel_sup = effect_sup + effect_wel
gen effect_total  = effect_wel_sup + effect_gross
gen year2=year*2

gen effect_sup_2 = effect_sup/effect_total
gen effect_wel_2 = effect_wel/effect_total
gen effect_gross_2 = effect_gross/effect_total


replace effect_sup_2=. if effect_sup_2==0


graph bar effect_sup_2 effect_wel_2 effect_gross_2, over(year) stack /*
*/legend(order(1 "New Hope supplement" 2 "Welfare" 3 "Earnings" )) /*
*/ bar(1, lwidth(medthick)  lcolor(black) fcolor(white))/*
*/ bar(2, lwidth(medium) lcolor(black))/*
*/ bar(3, lcolor(black) fcolor(ltblue)) /*
*/ ytitle("Change in income (2003 dollars)")  b1title("Years after random assignment") /*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) /*
*/plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid) yline(0, lpattern(solid) lcolor(black)) /*
*/ yline(1, lpattern(dash) lcolor(black)) scale(1.2) 


graph export "$results/Income/income_decomposition.pdf", as(pdf) replace












