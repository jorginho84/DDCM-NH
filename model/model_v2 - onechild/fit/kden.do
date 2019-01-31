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

twoway (kdensity points_0,lpattern(solid)) (kdensity points_1,lpattern(dash)),/*
*/scheme(s2mono) legend(order(1 "Treatment" 2 "Control")  )/*
*/ytitle(Density) xtitle(Factor)/*
*/graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white)) /*
*/ ylabel(, nogrid)  

graph export "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/ate_theta_factor.pdf", as(pdf) replace
