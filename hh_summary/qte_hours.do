/*
This do-file computes QTE on hours worked
*/

global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"

/*
robust SE for small samples. Set to hc3 for more conservatives. 

See Angrist and Pischke fotr more information
"robust" SE can be misleading when the sample size is small and there is no much heteroskedasticity.
*/
local SE="hc2"

clear
clear matrix
clear mata
set more off
set maxvar 15000

use "$databases/CFS_original.dta", clear
qui: do "$codes/data_cfs.do"

keep sampleid p_assign p_radatr piinvyy /*
*/ pthwjbf1 /*Hours worked away home (CFS)
*/r*smof1 r*syrf1 r*atjf1 r*emof1 r*eyrf1 r*hwsf1 r*hwef1 /*Year 2 variables*/

*date of RA+2 \approx date of year-2 interview
replace p_radatr=19000000+ p_radatr
tostring p_radatr, force replace
gen date_ra=mofd(date(p_radatr,"YMD"))
gen quarter_ra=qofd(date(p_radatr,"YMD"))
format %tm date_ra
gen date_survey=date_ra+24
format %tm date_survey


*Dropping individuals with no year-2 survey
drop if piinvyy==" "

*Rename for easier reshaping

forvalues x=1/19{
	rename r`x'smof1 start_month`x'
	rename r`x'syrf1 start_year`x'
	rename r`x'atjf1 still`x'
	rename r`x'emof1 end_month`x' 
	rename r`x'eyrf1 end_year`x'
	rename r`x'hwsf1 hours_start`x' 
	rename r`x'hwef1 hours_end`x'
}

*Reshaping by spell number (19)
reshape long start_month start_year still end_month end_year hours_start hours_end, i(sampleid) j(spell)
destring hours* still, replace force


*Start and end in month-year format
gen start_aux= start_year + "m"+ start_month
replace start_aux="" if start_year=="" | start_month==""
gen end_aux=end_year+"m"+end_month
replace end_aux="" if end_year=="" | end_month==""
	
*in %tm format
gen start=monthly(start_aux,"YM")
gen end=monthly(end_aux,"YM")
format %tm start
format %tm end
drop start_aux end_aux


*Month and year of each spell: missing = 0's
forvalues y=1994/1998{
	forvalues mm=1/12{
	gen hours`y'm`mm'=hours_end if ( start<=monthly("`y'm`mm'","YM") & end>=monthly("`y'm`mm'","YM") )  | /*
	*/( start<=monthly("`y'm`mm'","YM")  & still==1 & monthly("`y'm`mm'","YM")==date_survey )
	
	replace hours`y'm`mm'=. if monthly("`y'm`mm'","YM")>date_survey
	}

}



*Reshape long again for month/year
drop hours_start hours_end
reshape long hours, i(sampleid spell) j(month_aux) string

*SD of hours (across periods)
*sum hours
*local sd_hours=r(sd)

*Collapse my month: and we are done! (this doesn't consider 0s)
keep sampleid p_assign month_aux hours date_ra quarter_ra
gen month=monthly(month_aux, "YM")
format month %tm
replace hours=. if hours==0
collapse (mean) hours (first) p_assign date_ra quarter_ra, by(sampleid month)

*Collapse by quarter
gen quarter = qofd(dofm(month))
drop month
replace hours=0 if hours==.
sort sampleid quarter
collapse (mean) hours (first) p_assign date_ra quarter_ra, by(sampleid quarter)

*Quarter since RA
gen q_ra = quarter - quarter_ra

*Reshape again to build the graph using collapse
replace q_ra=q_ra+7 /*trick to reshape. from q=-2 is full sample*/
keep hours sampleid q_ra p_assign
reshape wide hours, i(sampleid) j(q_ra)

*recovering curremp
sort sampleid
tempfile data_aux
save `data_aux', replace
use "$databases/CFS_original.dta", clear
qui: do "$codes/data_cfs.do"
keep sampleid curremp
merge 1:1 sampleid using `data_aux'
drop if _merge!=3
drop _merge
	


*Obtaining control variables
do "$codes/income/Xs.do"
local control_var age_ra i.marital i.ethnic d_HS2 higrade i.pastern2
	

*Earnings less than 1000
gen d_e_low =  pastern2<=4
	
*Dropping 50 observations with no children
do "$codes/time/drop_50.do"

*Don't have full sample here
drop hours0-hours4 hours16-hours24

*Getting data of employment from UI
tempfile data_aux1
save `data_aux1', replace

use "$results/Time/data_emp.dta", clear
merge 1:1 sampleid using `data_aux1'
keep if _merge==3
drop _merge

*One additional clean up
forvalues x=5/15{
	local y = `x'-1 /*getting the right time for emp*/
	replace hours`x'=0 if emp`y'==0
}


*dummy RA for ivqte
gen d_ra = .
replace d_ra = 1 if p_assign=="E"
replace d_ra = 0 if p_assign=="C"
*************************************************************
****Exercise 5: quantile regressions with ht=0 (0-2 years)
preserve
keep hours* d_ra sampleid
reshape long hours, i(sampleid) j(quarter)


qui: ivqte hours (d_ra), quantiles(.05 .1 .15 .2 .25 .3 .35 .4 .45 .5 .55 .60 .65 .7 .75 .8 .85 .90 .95) variance
		
forvalues q = 1/19{
	if `q'==1{
		mat betas_5 = (_b[Quantile_`q'],_b[Quantile_`q'] - invnorm(0.975)*_se[Quantile_`q'],/*
	*/ _b[Quantile_`q'] + invnorm(0.975)*_se[Quantile_`q'])
		qui: test Quantile_`q'=0
		mat pvalues_5=r(p)
	}
	else{
		mat betas_5 = betas_5\(_b[Quantile_`q'],_b[Quantile_`q'] - invnorm(0.975)*_se[Quantile_`q'],/*
	*/ _b[Quantile_`q'] + invnorm(0.975)*_se[Quantile_`q'])
		qui: test Quantile_`q'=0
		mat pvalues_5=pvalues_5\r(p)

	}
	
}
restore


*****The Graph*****
svmat betas_5
svmat pvalues_5
drop if betas_51==.
egen quant = seq()



gen mean_aux_5=betas_51 if pvalues_51<=0.05



twoway (connected betas_51 quant , msymbol(circle) mlcolor(blue) mfcolor(white) ) /*
*/ (scatter mean_aux_5 quant , msymbol(circle) mlcolor(blue) mfcolor(blue)) /* 
*/(line betas_52 quant ,lpattern(dash)) /*
*/(line betas_53 quant ,lpattern(dash)),/*
*/ yline(0, lcolor(black))/*
*/ytitle("Impact on hours") xtitle("Quantile") legend(off)/*
*/ xlabel( 2 "10" 4 "20" 6 "30" 8 "40" 10 "50" 12 "60" 14 "70" 16 "80" 18 "90", noticks) /*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) /*
*/plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ ylabel(, nogrid)scale(1.2) scheme(s2mono) 

graph export "$results/HH_summary/hours_diff_experiment5.pdf", as(pdf) replace

	
