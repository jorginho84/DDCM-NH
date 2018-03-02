/*

This do file plots kdensity graphs
*/

clear
program drop _all
clear matrix
clear mata
set more off
set maxvar 15000
set matsize 2000


use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/theta_sample.dta", clear

*Drop 1% and 99%

foreach x in 2 5 8{
	preserve
	xtile pct_y`x' = theta_y`x', nq(100)
	drop if pct_y`x'==1 | pct_y`x'==100

	qui: sum theta_y`x' if d_RA==0
	local mean_0 = r(mean)

	qui: sum theta_y`x' if d_RA==1
	local mean_1 = r(mean)

	twoway (kdensity theta_y`x' if d_RA==0,lpattern(solid)) /*
	*/ (kdensity theta_y`x' if d_RA==1,lpattern(dash)),/*
	*/scheme(s2mono) legend(order(1 "Control" 2 "Treatment")  )/*
	*/ytitle(Density) xtitle(Factor)/*
	*/graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white)) /*
	*/ ylabel(, nogrid)  xline(`mean_0', lcolor(red)) xline(`mean_1', lcolor(red) lpattern(dash)) /*
	*/ xlabel(-7(4)7)

	graph export "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/ate_theta_factor_y`x'.pdf", as(pdf) replace
	restore

}

clear

*erase "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/theta_sample.dta"

exit, STATA clear



