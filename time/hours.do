/*
This do-file computes the impact of NH on hours worked using data from the NH survey

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


/*
Choose:
year2=1: runs  year 2. This will produce a graph.
year5_8=1: runs years 5 and 8. This will produce a table

*/

local year2=1
local year5_8=0

*Scale of graphs
*local scale = 1


/*
Set control=1 if regressions control for X's
*/

local controls=1


if `year2'==1{

use "$databases/CFS_original.dta", clear
qui: do "$codes/data_cfs.do"
/*
********************************************************************************
*Recovering information on children
sort sampleid
tempfile data_cfs
save `data_cfs', replace

use "$databases/Youth_original2.dta", clear
keep sampleid child zboy agechild
destring sampleid, force replace
reshape wide zboy agechild, i(sampleid) j(child)
sort sampleid
merge 1:1 sampleid using `data_cfs'

keep if _merge==3
drop _merge

*Keep if at least one of the two children is a boy and young
keep if (zboy1==1 | zboy2==1) & (agechild1<=7 | agechild2<=7)
drop zboy* agechild*

********************************************************************************
*/

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
if `controls'==1{

	do "$codes/income/Xs.do"
	local control_var age_ra i.marital i.ethnic d_HS2 higrade i.pastern2
	
}

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


*Estimates
local start = 7
forvalues x=`start'/15{
	
	****Exercise 1: hours for those who h0
	qui xi: reg hours`x' i.p_assign `control_var' if hours`x'>0, vce(`SE')
			
	if `x'==`start'{
		mat betas_1 = (_b[_Ip_assign_2],_b[_Ip_assign_2] - invttail(e(df_r),0.025)*_se[_Ip_assign_2],/*
			*/ _b[_Ip_assign_2] + invttail(e(df_r),0.025)*_se[_Ip_assign_2])
		qui: test _Ip_assign_2=0
		mat pvalues_1=r(p)
	}
		
	else{

		mat betas_1 = betas_1\(_b[_Ip_assign_2],_b[_Ip_assign_2] - invttail(e(df_r),0.025)*_se[_Ip_assign_2],/*
			*/ _b[_Ip_assign_2] + invttail(e(df_r),0.025)*_se[_Ip_assign_2])
		qui: test _Ip_assign_2=0
		mat pvalues_1=pvalues_1\r(p)
	}

	****Exercise 2: hours for those who h0>0 & employed at baseline
	qui xi: reg hours`x' i.p_assign `control_var' if hours`x'>0 & curremp=="Yes", vce(`SE')
			
	if `x'==`start'{
		mat betas_2 = (_b[_Ip_assign_2],_b[_Ip_assign_2] - invttail(e(df_r),0.025)*_se[_Ip_assign_2],/*
			*/ _b[_Ip_assign_2] + invttail(e(df_r),0.025)*_se[_Ip_assign_2])
		qui: test _Ip_assign_2=0
		mat pvalues_2=r(p)
	}
		
	else{

		mat betas_2 = betas_2\(_b[_Ip_assign_2],_b[_Ip_assign_2] - invttail(e(df_r),0.025)*_se[_Ip_assign_2],/*
			*/ _b[_Ip_assign_2] + invttail(e(df_r),0.025)*_se[_Ip_assign_2])
		qui: test _Ip_assign_2=0
		mat pvalues_2=pvalues_2\r(p)
	}

	****Exercise 3: hours for those who h0>0 & employed at baseline & low earnings
	qui xi: reg hours`x' i.p_assign `control_var' if hours`x'>0 & curremp=="Yes" /*
	*/ & d_e_low==1, vce(`SE')
			
	if `x'==`start'{
		mat betas_3 = (_b[_Ip_assign_2],_b[_Ip_assign_2] - invttail(e(df_r),0.025)*_se[_Ip_assign_2],/*
			*/ _b[_Ip_assign_2] + invttail(e(df_r),0.025)*_se[_Ip_assign_2])
		qui: test _Ip_assign_2=0
		mat pvalues_3=r(p)
	}
		
	else{

		mat betas_3 = betas_3\(_b[_Ip_assign_2],_b[_Ip_assign_2] - invttail(e(df_r),0.025)*_se[_Ip_assign_2],/*
			*/ _b[_Ip_assign_2] + invttail(e(df_r),0.025)*_se[_Ip_assign_2])
		qui: test _Ip_assign_2=0
		mat pvalues_3=pvalues_3\r(p)
	}

	****Exercise 4: hours for those who h0>0 & employed at baseline & high earnings
	qui xi: reg hours`x' i.p_assign `control_var' if hours`x'>0 & curremp=="Yes" /*
	*/ & d_e_low==0, vce(`SE')
			
	if `x'==`start'{
		mat betas_4 = (_b[_Ip_assign_2],_b[_Ip_assign_2] - invttail(e(df_r),0.025)*_se[_Ip_assign_2],/*
			*/ _b[_Ip_assign_2] + invttail(e(df_r),0.025)*_se[_Ip_assign_2])
		qui: test _Ip_assign_2=0
		mat pvalues_4=r(p)
	}
		
	else{

		mat betas_4 = betas_4\(_b[_Ip_assign_2],_b[_Ip_assign_2] - invttail(e(df_r),0.025)*_se[_Ip_assign_2],/*
			*/ _b[_Ip_assign_2] + invttail(e(df_r),0.025)*_se[_Ip_assign_2])
		qui: test _Ip_assign_2=0
		mat pvalues_4=pvalues_4\r(p)
	}


	


}

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


*For the first 4 experiments
forvalues x=1/4{
	svmat betas_`x'	
	svmat pvalues_`x'	
	
}


*Graphs for the first 4 experiments
preserve
drop if betas_11==.
egen quarter = seq()
replace quarter=quarter-1 /*back to the original number*/



*After this month, there are no records
*drop if quarter>9

*Recovering matrix of pvalues (fake labels for figure)

*The experiment loop
forvalues x=1/4{

	
	*Labels for significance
	gen mean_aux_`x'=betas_`x'1 if pvalues_`x'1<=0.05

	twoway (connected betas_`x'1 quarter , msymbol(circle) mlcolor(blue) mfcolor(white) ) /*
	*/ (scatter mean_aux_`x' quarter , msymbol(circle) mlcolor(blue) mfcolor(blue)) /* 
	*/(line betas_`x'2 quarter ,lpattern(dash)) /*
	*/(line betas_`x'3 quarter ,lpattern(dash)),/*
	*/ yline(0, lcolor(black))/*
	*/ytitle("{&Delta}hours") xtitle("Quarters since RA") legend(off)/*
	*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) /*
	*/plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
	*/ ylabel(, nogrid)scale(1.2) scheme(s2mono) 

	graph export "$results/Time/hours_diff_experiment`x'.pdf", as(pdf) replace

	
	
}


*Experiment #5 (QTE)
restore
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
*/ytitle("{&Delta}hours") xtitle("Quantile") legend(off)/*
*/ xlabel( 2 "10" 4 "20" 6 "30" 8 "40" 10 "50" 12 "60" 14 "70" 16 "80" 18 "90", noticks) /*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) /*
*/plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ ylabel(, nogrid)scale(1.2) scheme(s2mono) 

graph export "$results/Time/hours_diff_experiment5.pdf", as(pdf) replace

	
}

*Show me the sd of hours

********************************************************************************
/*
*YEARS 5 AND 8

Only for those employed (the variables piq66 and epi54 take missing values 
when not work working)

*/
********************************************************************************

if `year5_8'==1{

use "$databases/CFS_original.dta", clear
qui: do "$codes/data_cfs.do"
/*
********************************************************************************
*Recovering information on children
sort sampleid
tempfile data_cfs
save `data_cfs', replace

use "$databases/Youth_original2.dta", clear
keep sampleid child zboy agechild
destring sampleid, force replace
reshape wide zboy agechild, i(sampleid) j(child)
sort sampleid
merge 1:1 sampleid using `data_cfs'

keep if _merge==3
drop _merge

*Keep if at least one of the two children is a boy and young
keep if (zboy1==1 | zboy2==1) & (agechild1<=7 | agechild2<=7)
drop zboy* agechild*

********************************************************************************
*/
*These are the hours variables
destring piq66 epi54, replace force
rename piq66 hours_t4
rename epi54 hours_t7


*Ra indicator
gen RA=1 if p_assign=="E"
replace RA=2 if p_assign=="C"
label define ra_lbl 1 "Treatment" 2 "Control"
label values RA ra_lbl

*Indicates year-x missing
gen d_year5=piinvdd==" "
gen d_year8=epiinvyy==" "


*****Employment variables*****
destring piinvyy epiinvyy, force replace
destring piq49 piq50 piq51 piq54 piq55 piq56, replace force 
gen emp_y4= piq49==7 | piq50==4 | piq51==6 | piq54==3 | piq55==5 | piq56==2
replace emp_y4=. if  piinvyy==.

*worked last 12 months according to survey y8
destring epi33 epi34 epi35 epi37 epi38 epi39, force replace
gen emp_y7= epi33==7 | epi34==4 | epi35==6 | epi37==3 | epi38==5 | epi39==2
replace emp_y7=. if epiinvyy==.

replace hours_t4=0 if emp_y4==0
replace hours_t4=. if piinvyy==.

replace hours_t7=0 if emp_y7==0
replace hours_t7=. if epiinvyy==.





*Obtaining control variables
if `controls'==1{

	qui: do "$codes/income/Xs.do"
	local control_var age_ra i.marital i.ethnic d_HS higrade i.pastern2
	
}



tempfile data_hours
save `data_hours', replace
use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Income/data_income.dta", clear
merge 1:m sampleid using `data_hours'
keep if _merge==3
drop _merge

drop total_income_y0 gross_y0 gross_nominal_y0 grossv2_y0 employment_y0 /*
*/ fs_y0 afdc_y0 sup_y0
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

}


foreach x of numlist 4 7{
	replace hours_t`x'=0 if grossv2_y`x'==0 & hours_t`x'!=.
}


*For years 4 and 7, adjust for proportion of hours work

foreach x of numlist 4 7{
	replace hours_t`x'=hours_t`x'*employment_y`x'
}






*Regressions and table
local j=7
local y=5
foreach variable of varlist hours_t4 hours_t7{


	*qui ttest `variable' if employment_year`y'==1, by(RA)
	qui ttest `variable' if `variable'>0, by(RA)
	mat A=(r(mu_1),r(mu_2),0\r(sd_1), r(sd_2), 0)

	 xi: reg `variable' i.p_assign if `variable'>0, vce(`SE')
	mat variance=e(V)
	mat A[2,3]=variance[1,1]^0.5/*replace it with S.E.*/
	mat A[1,3]=_b[_Ip_assign_2]
	qui test _Ip_assign_2=0
	mat b_aux=(r(p)\0)
	mat data=A,b_aux/*add p-value*/

	
	*The table
	putexcel C`j'=matrix(data) using "$results/Time/hours_years5_8", sheet("data") modify
	
	local j=`j'+2
	local y=`y'+3


}



}

