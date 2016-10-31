/*
This do-file performs a mediation analysis.
The basic equation:

Y_t=+\tau_0 \tau*RA + alpha_1*CC+ \alpha_2*Income+\alpha_3*l* + X'\beta \epsilon

l*=leisure\times \tau_t: is a measure of active time with the child

\tau_t: quality time

note: the regression better fit when using lt (leisure=24-8-h_t) instead
of l_t*.



Doing this for t=2,5,8 (years after RA)

CC: child care during the first two years of the experiment
X: child age at baseline, mother's education (other X's from baseline analysis)

*/



global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"

/*
robust SE for small samples. Set to hc3 for more conservatives. 

See Angrist and Pischke for more information
"robust" SE can be misleading when the sample size is small and there is no much heteroskedasticity.
*/
local SE="hc2"


clear
clear matrix
clear mata
set maxvar 15000
set more off


use "$databases/Youth_original2.dta", clear
do "$codes/data_youth.do"

keep sampleid child p_assign zboy agechild /* identifiers
*/ tcsbs tcsis tcsts tcstot tacad  tq17* /* outcomes from year-2
*/ c68* c69* /*CC use 
*/ t2q17*/* teachers reports: SSRS academic subscale (a-j), year 5
*/ etsq13*/* teachers reports: SSRS academic subscale (a-j) year 8
*/ y41 y42 y44 y45 y47 y48 y50 y51 /*Time variables: young
*/ o31 o32 o33 o35 o41 o44 o46 o48 /*Time variables: old*/


*keep if agechild<=7

*Choose sample=1 if the analysis should be done on the same sample for all years
local sample=0


********************************************************************************************************
****************Child care use variable: d_CC***********************************************************
********************************************************************************************************

destring sampleid, force replace
sort sampleid
tempfile youth
save `youth', replace


use "$databases/CFS_original.dta", clear
do "$codes/data_cfs.do"

*Note: hoours worked are used later
keep sampleid p_assign p_radatr /* Identifiers*/


sort sampleid
merge 1:m sampleid using `youth' /*50 adults with no children, 2 children with no adults*/
keep if _merge==3
drop _merge


*Negative variables: time
foreach variable of varlist y42 y44 y50 o31 o41 o44 o46{
	gen `variable'_neg=1 if `variable'==3
	replace `variable'_neg=3 if `variable'==1
	drop `variable'
	rename `variable'_neg `variable'

}

*Three categories for the old

foreach variable of varlist o31 o32 o33 o35 o41 o44 o46 o48{
	gen `variable'_new=1 if `variable'==1 | `variable'==2
	replace `variable'_new=2 if `variable'==3 | `variable'==4
	replace `variable'_new=3 if `variable'==5
	drop `variable'
	rename `variable'_new `variable'

}



*Computing measures of time
egen time_y=rowmean(y41 y42 y44 y45 y47 y48 y50 y51)
egen time_o=rowmean(o31 o32 o33 o35 o41 o44 o46 o48)
gen time=time_y
replace time=time_o if time==.




gen CC=1 if c68g==0 /*NO ARRANGEMENTS*/
replace CC=2 if (c68a==1 & c69a_2==child) | (c68a==1 & c69a_4==child) /*HEAD START*/
replace CC=3 if (c68b==1 & c69b_2==child) | (c68b==1 & c69b_4==child) /*Preschool, nursey, or CC other than Head Start*/
replace CC=4 if (c68c==1 & c69c_2==child) | (c68c==1 & c69c_4==child) | (c68c==1 & c69c_6==child) | (c68c==1 & c69c_8==child) /*Extended day program*/
replace CC=5 if (c68d==1 & c69d_2==child) | (c68d==1 & c69d_4==child) | (c68d==1 & c69d_6==child) /*Another CC other than someone's home*/
replace CC=6 if (c68e==1 & c69e_2==child) | (c68e==1 & c69e_4==child) | (c68e==1 & c69e_6==child) | (c68e==1 & c69e_6==child)/*
*/| (c68e==1 & c69e_6==child) /*Any person other than household member"*/
replace CC=7 if (c68f==1 & c69f_2==child) | (c68f==1 & c69f_4==child) | (c68f==1 & c69f_6==child) | (c68f==1 & c69f_6==child)/*
*/| (c68f==1 & c69f_6==child)/*Another household member*/

label define CC_lbl 1 "NO ARRANGEMENTS" 2 "HEAD START" 3 "Preschool, nursey, or CC other than Head Start" 4 "Extended day program"/*
*/ 5 "Another CC other than someone's home" 6 "Any person other than household member" 7 "Another household member"
label values CC CC_lbl

*CHild care: Head Start, Preschool, Nursery, or CC, extended day program, another CC other than someone's home
gen d_CC=1 if CC==2 | CC==3 | CC==4 | CC==5
replace d_CC=0 if CC==1 | CC==6 | CC==7 /*no arrangements, a hh member, someone other than hh member*/

********************************************************************************************************
**************HOURS WORKED******************************************************************************
********************************************************************************************************
/*
In this version of hours worked, I'm not conditioning on being employed (leaving 0's)
*/

sort sampleid
tempfile data_aux
save `data_aux', replace

use "$databases/CFS_original.dta", clear
do "$codes/data_cfs.do"

*C1, piinvdd, epiinvdd: to use it as an indicator of year-2, 5 respondent

keep sampleid p_assign p_radatr c1 piinvdd epiinvdd /*
*/ pthwjbf1 /*Hours worked away home (CFS)
*/r*smof1 r*syrf1 r*atjf1 r*emof1 r*eyrf1 r*hwsf1 r*hwef1 /*Year 2 variables*/

*Those who answered the year 2,8, interview
gen year2=c1!=" "
gen year5=piinvdd!=" "
gen year8=epiinvdd!=" "

*date of RA+2 \approx date of year-2 interview
replace p_radatr=19000000+ p_radatr
tostring p_radatr, force replace
gen date_ra=mofd(date(p_radatr,"YMD"))
format %tm date_ra
gen date_survey=date_ra+24
format %tm date_survey


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


*Month and year of each spell
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

*Collapse my month: and we are done!
keep sampleid p_assign month_aux hours date_ra year2 year5 year8
gen month=monthly(month_aux, "YM")
format month %tm

/*
*For each individual, average hours by month.
I am not weighting by the lenght of each spell during the month. 
*/
collapse (mean) hours (first) p_assign date_ra year2 year5 year8, by(sampleid month)



*Consider 0's for those who answer the year-2 interview
replace hours=0 if hours==. & year2==1


*Months since RA
gen months_ra=month-date_ra


*Reshape again to build the graph using collapse
replace months_ra=months_ra+23 /*trick to reshape*/
keep hours sampleid months_ra p_assign year2 year5 year8
reshape wide hours, i(sampleid) j(months_ra)

*Back to the original name
drop hours0-hours22

forvalues x=23/75{
	local y=`x'-23
	rename hours`x' hours`y'

}

*Note: after 24 (two years after RA), hours=0: survey asks only up to that year. So we're good.

sort sampleid

merge 1:m sampleid using `data_aux'
keep if _merge==3 /*50 adults do not have children*/
drop _merge

*Years 5 and 8
sort sampleid
tempfile data_hours_aux
save `data_hours_aux', replace

use "$databases/CFS_original.dta", clear
do "$codes/data_cfs.do"
keep sampleid piq66 epi54
destring piq66 epi54, force replace

sort sampleid
merge 1:m sampleid using `data_hours_aux' /*50 adults do not have children*/
keep if _merge==3
drop _merge




*******************************************************************************************
*************************************UI INCOME********************************************
*******************************************************************************************

sort sampleid
tempfile data_aux2
save `data_aux2', replace

*Use the CFS study
use "$databases/CFS_original.dta", clear
do "$codes/data_cfs.do"


keep sampleid p_assign p_radatr cstartm curremp /*
*/ern*q* sup*q* csjm9* wwq* fsq* /*UI earnings, NH supplement, CSJ's, AFDC/W-2 and Food stamps */ 


*Date of RA
replace p_radatr=p_radatr+19000000
tostring p_radatr, force replace

sort sampleid
tempfile data_income1
save `data_income1', replace

**********************************
*CSJ: months and quarters since RA
**********************************

*Month of RA
gen ra_month=mofd(date(p_radatr,"YMD"))
format ra_month %tm
tab ra_month

*Renaming CSJ calendar-time variables
forvalues y=94/97{

	local m=1
	foreach month in "01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12"{
		rename csjm`y'`month' csj19`y'm`m'
		local m=`m'+1
	}
	
} 


keep csj19* sampleid ra_month
reshape long csj, i(sampleid) j(month_aux) string
gen month=monthly(month_aux, "YM")
format month %tm


*months since RA
gen months_ra=month-ra_month
keep months_ra sampleid csj
tab months_ra


*Reshape again 
replace months_ra=months_ra+23
reshape wide csj, i(sampleid) j(months_ra)

*back to the original name
forvalues x=0/22{
	drop csj`x' 
}


forvalues x=23/63{
	local y=`x'-23
	rename csj`x' csj`y'
}

*Merging with the original data
sort sampleid
tempfile data_income
save `data_income', replace

use `data_income1', clear

*merging
merge 1:1 sampleid using `data_income'
drop _merge
drop csjm*

*CSJ: quarters since RA

local m0=0
forvalues q=0/13{
	local m1=`m0'+1
	local m2=`m1'+1
	
	
	if `q'==13{
		egen csj_q`q'=rowtotal(csj`m0' csj`m1')
	}
	
	else {
		egen csj_q`q'=rowtotal(csj`m0' csj`m1' csj`m2')
	}
	
	local m0=`m0'+3

}

*******************************
*UI Earnings: quarters since RA
*******************************
sort sampleid
tempfile data_income2
save `data_income2', replace

*Quarter of RA
gen ra_quarter=qofd(date(p_radatr,"YMD"))
format ra_quarter %tq
tab ra_quarter

*Renaming to reshape
rename ern4q93 ern1993q4

local nn=1
forvalues y=94/99{
	forvalues q=1/4{

		rename ern`q'q`y' ern19`y'q`q'
		
	}
}

local yy=0
forvalues y=2000/2003{
	forvalues q=1/4{

		rename ern`q'q0`yy' ern200`yy'q`q' 
				
	}

local yy=`yy'+1
}

*I DON"T HAVE EARNINGS FOR 98Q1: leave them as missing.
destring ern1998q1, replace force


*Reshaping to build a panel
keep ern* sampleid ra_quarter
reshape long ern, i(sampleid) j(quarter_aux) string
gen quarter=quarterly(quarter_aux, "YQ")
format quarter %tq

*Quarters since RA
gen quarters_ra=quarter-ra_quarter
keep quarters_ra sampleid ern
tab quarters_ra/*this is to see how many obs*/


*Reshape again
replace quarters_ra=quarters_ra+8/*trick to reshape*/
reshape wide ern, i(sampleid) j(quarters_ra) 


*back to the original name
drop ern0 ern1 ern2 ern3 ern4 ern5 ern6 ern7 

forvalues x=8/45{
	local y=`x'-8
	rename ern`x' earn_q`y'
}

*Merging with original data
sort sampleid
merge 1:1 sampleid using `data_income2'
drop _merge ern1* ern2* ern3* ern4*


**********************************
*NH supplement: quarters since RA
**********************************
/*
There is a small discrepancy between my measure and the NH's variable: one 
individual received supplement in quarters 14 and 15. I choose to use my measure.
*/


sort sampleid
tempfile data_income3
save `data_income3', replace

*Quarter of RA
gen ra_quarter=qofd(date(p_radatr,"YMD"))
format ra_quarter %tq
tab ra_quarter

destring sup*q*, replace force

*Renaming to reshape
local nn=1
forvalues y=94/99{
	forvalues q=1/4{
		
		replace sup`y'q`q'=0 if sup`y'q`q'==.
		rename sup`y'q`q' sup19`y'q`q'
		
	}
}


forvalues q=1/4{
	replace sup00q`q'=0 if sup00q`q'==.
	rename sup00q`q' sup2000q`q' 
				
}



*Reshaping to build a panel
keep sup199* sup2000* sampleid ra_quarter
reshape long sup, i(sampleid) j(quarter_aux) string
gen quarter=quarterly(quarter_aux, "YQ")
format quarter %tq

*Quarters since RA
gen quarters_ra=quarter-ra_quarter
keep quarters_ra sampleid sup
tab quarters_ra/*this is to see how many obs*/


*Reshape again
replace quarters_ra=quarters_ra+7/*trick to reshape*/
reshape wide sup, i(sampleid) j(quarters_ra) 

*back to the original name
drop sup0 sup1 sup2 sup3 sup4 sup5 sup6 

forvalues x=7/32{
	local y=`x'-7
	rename sup`x' sup`y'
}

*Merging with original data
sort sampleid
merge 1:1 sampleid using `data_income3'
drop _merge supq* supi* sup*q*
drop sup16 sup17 sup18 sup19 sup20 sup21 sup22 sup23 sup24 sup25 /*these are 0's*/ 


******************************************
*FOOD STAMPS and AFDC BY QUARTERS SINCE RA
******************************************

*Food stamps

qui destring fsq33 fsq34 fsq35 fsq36 fsq37, replace force

*AFDC and W-2 (wisconsin works)
qui destring wwq33 wwq34 wwq35 wwq36 wwq37, replace force 

**********************************
*Total income by quarter
**********************************

*Total income: from 1-37 (quarters 0 not available in FS and AFDC)

/*
Unil quarter 32 I have 745 observations.
*/

forvalues q=1/37{

	if `q'<=13{
		egen total_income_q`q'=rowtotal(earn_q`q' csj_q`q' sup`q' fsq`q' wwq`q')
	}
	
	else if `q'>=14 & `q'<=15{
		egen total_income_q`q'=rowtotal(earn_q`q' sup`q' fsq`q' wwq`q')
	}
	
	else{
		egen total_income_q`q'=rowtotal(earn_q`q' fsq`q' wwq`q')
	}

}


*I'm keeping earn_ to adjust for employment in hours worked (years 5 and 8)
keep total_income* earn_q* sampleid
sort sampleid


merge 1:m sampleid using `data_aux2'
keep if _merge==3
drop _merge

*************************************************************************************
*************************************************************************************
/*

Baseline variables: X's

*/
*************************************************************************************
*************************************************************************************
sort sampleid
tempfile data_aux3
save `data_aux3', replace


use "$databases/CFS_original.dta", clear
do "$codes/data_cfs.do"


keep p_assign sampleid p_radatr p_bdatey p_bdatem p_bdated b_bdater bifage p_bdatey p_bdatem gender ethnic marital higrade /*
*/pastern2 work_ft curremp currwage higrade c1 piinvyy epiinvyy 

*Constructing age at RA (bifage has 24 odd values)

*Date at RA
tostring p_radatr, gen(date_ra_aux)
gen date_ra_aux2="19"+date_ra_aux
gen date_ra = date(date_ra_aux2, "YMD")
format date_ra %td

*Birthdate
tostring p_bdatey p_bdatem p_bdated, gen(p_bdatey_aux p_bdatem_aux p_bdated_aux)

foreach x of varlist p_bdatem p_bdated{
	replace `x'_aux="0"+`x'_aux if `x'<10
}

gen bday_aux="19"+p_bdatey_aux + p_bdatem_aux + p_bdated_aux
gen bday = date(bday_aux, "YMD")
format bday %td

*Age at RA
generate age_ra = floor(([ym(year(date_ra), month(date_ra)) - ym(year(bday), month(bday))] - [1 < day(bday)]) / 12)

*Education
gen cat_educ=1 if higrade<12
replace cat_educ=2 if higrade==12
replace cat_educ=3 if higrade>12

label define cat_educ_lcl 1 "Less than HS diploma" 2 "HS" 3 "More than HH"
label values cat_educ cat_educ_lcl

keep sampleid age_ra gender ethnic marital cat_educ
sort sampleid

merge 1:m sampleid using `data_aux3'
keep if _merge==3
drop _merge






**************************************************************************************
**************************************************************************************
**************************************************************************************
/*
Generating Inputs
*/
**************************************************************************************
**************************************************************************************
**************************************************************************************



*Average annual income (years 1/2)
gen income_y1=total_income_q1+total_income_q2+total_income_q3+total_income_q4
gen income_y2=total_income_q5+total_income_q6+total_income_q7+total_income_q8
egen income_y1_2=rowmean(income_y1 income_y2)

*Average annual income years 3,4,5
gen income_y3=total_income_q9+total_income_q10+total_income_q11+total_income_q12
gen income_y4=total_income_q13+total_income_q14+total_income_q15+total_income_q16
gen income_y5=total_income_q17+total_income_q18+total_income_q19+total_income_q20
egen income_y3_5=rowmean( income_y3 income_y4 income_y5)

*Average annual income years 6,7,8
gen income_y6=total_income_q21+total_income_q22+total_income_q23+total_income_q24
gen income_y7=total_income_q25+total_income_q26+total_income_q27+total_income_q28
gen income_y8=total_income_q29+total_income_q30+total_income_q31+total_income_q32
egen income_y6_8=rowmean( income_y6 income_y7 income_y8)


*log of income (loose 5 obs)
gen log_income_y1_2=log(income_y1_2)
gen log_income_y3_5=log(income_y3_5)
gen log_income_y6_8=log(income_y6_8)

*Average weekly hours (years 1/2). Including 0's for all those who answer year 2
egen hours_y1_2=rowmean(hours1 hours2 hours3 hours4 hours5 hours6 hours7 hours8/* 
*/ hours9 hours10 hours11 hours12 hours13 hours14 hours15 hours16 hours17 hours18 hours19/*
*/ hours20 hours21 hours22 hours23 hours24)

*These are year 2 and 5 hours: piq66 epi54
rename piq66 hours_y3_5_aux
rename epi54 hours_y6_8_aux

*Including 0's for those who answer the surveys
replace hours_y3_5_aux=0 if hours_y3_5_aux==. & year5==1
replace hours_y6_8_aux=0 if hours_y6_8_aux==. & year8==1

*Adjusting for unmeployment using UI records

*employment indicators (years 3-8)
forvalues x=9/32{
	gen employment_q`x'=earn_q`x'>0 & earn_q`x'!=.
	
	if `x'<=20{
		gen emp_hours_q`x'=employment_q`x'*hours_y3_5_aux if hours_y3_5_aux!=.
	}
	else{
		gen emp_hours_q`x'=employment_q`x'*hours_y6_8_aux if hours_y6_8_aux!=.
	}
}

*Hours adjusted: I'm including 0's, for those who answer the interviews
egen hours_y3_5=rowmean(emp_hours_q9 emp_hours_q10 emp_hours_q11 emp_hours_q12 emp_hours_q13 emp_hours_q14 /* 
*/ emp_hours_q15 emp_hours_q16 emp_hours_q17 emp_hours_q18 emp_hours_q19 emp_hours_q20 )

egen hours_y6_8=rowmean(emp_hours_q21 emp_hours_q22 emp_hours_q23 emp_hours_q24 emp_hours_q25 emp_hours_q26 /*
*/ emp_hours_q27 emp_hours_q28 emp_hours_q29 emp_hours_q30 emp_hours_q31 emp_hours_q32)


*Sample indicators

*Year 2
qui xi: reg tq17a i.p_assign d_CC log_income_y1_2 hours_y1_2 age_ra i.zboy i.ethnic i.marital i.cat_educ agechild
predict y2 if tq17a!=. 
gen d_y2=y2!=.
drop y2


*Year 5
qui xi: reg t2q17a tq17a i.p_assign log_income_y3_5 hours_y3_5 /* Current inputs
*/ d_CC  log_income_y1_2 hours_y1_2 /* Past inputs
*/ age_ra i.zboy i.ethnic i.marital i.cat_educ agechild /*X's*/
predict y5 if t2q17a!=.
gen d_y5=y5!=.
drop y5

*Year 8
qui xi: reg etsq13a t2q17a i.p_assign log_income_y6_8 hours_y6_8 /* Current inputs
*/ d_CC  log_income_y3_5 hours_y3_5 log_income_y1_2 hours_y1_2 /* Past inputs
*/ age_ra i.zboy i.ethnic i.marital i.cat_educ agechild /*X's*/
predict y8 if etsq13a!=.
gen d_y8=y8!=.
drop y8


if `sample'==1{
	keep if d_y2==1 &  d_y5==1 & d_y8==1
}

stop

*******************************************************************************************************************
**********************************YEAR-2 REGRESSION****************************************************************
*******************************************************************************************************************

*leisure time
gen l_star_y2=(21-8-hours_y1_2)*time
gen l_y2=(21-8-hours_y1_2)

*ATE
qui xi: reg tq17a i.p_assign if d_y2==1
scalar ate=_b[_Ip_assign_2]

*Regression: can't do fixed effects b/c there is no variation in random assignment within family.
xi: reg tq17a i.p_assign d_CC log_income_y1_2 l_star_y2 age_ra i.zboy i.ethnic i.marital i.cat_educ agechild if d_y2==1
xi: reg tq17a i.p_assign d_CC log_income_y1_2 l_y2 age_ra i.zboy i.ethnic i.marital i.cat_educ agechild if d_y2==1

*saving coeffs
scalar n_y2=e(N)
scalar b_tau=_b[_Ip_assign_2]
scalar alpha_d_CC=_b[d_CC]
scalar alpha_log_income_y1_2=_b[log_income_y1_2]
scalar alpha_hours_y1_2=_b[l_star_y2]

*Contributions
foreach variable of varlist d_CC log_income_y1_2 hours_y1_2{
	qui xi: reg `variable' i.p_assign
	scalar delta_`variable'=_b[_Ip_assign_2]
	
	scalar cont_`variable'=_b[_Ip_assign_2]*alpha_`variable'
}

*This is ATE
display ate

*These are the contributions
display b_tau 
display cont_d_CC 
display cont_log_income_y1_2 
display cont_hours_y1_2

*In % terms: not using these
foreach variable in b_tau cont_d_CC cont_log_income_y1_2 cont_hours_y1_2{
	scalar `variable'_pp=`variable'*100/ate
}

display b_tau_pp 
display cont_d_CC_pp
display cont_log_income_y1_2_pp 
display cont_hours_y1_2_pp


*******************************************************************************************************************
**********************************YEAR-5 REGRESSION****************************************************************
*******************************************************************************************************************


*ATE
qui xi: reg t2q17a i.p_assign if d_y5==1
scalar ate_y5=_b[_Ip_assign_2]

*Regression: can't do fixed effects b/c there is no variation in random assignment within family.
xi: reg t2q17a tq17a i.p_assign log_income_y3_5 hours_y3_5 /* Current inputs
*/ d_CC  log_income_y1_2 hours_y1_2 /* Past inputs
*/ age_ra i.zboy i.ethnic i.marital i.cat_educ agechild  if d_y5==1/*X's*/

*saving coeff
scalar n_y5=e(N)
scalar b_tau_y5=_b[_Ip_assign_2]
scalar alpha_tq17a=_b[tq17a]
scalar alpha_log_income_y3_5=_b[log_income_y3_5]
scalar alpha_hours_y3_5=_b[hours_y3_5]
scalar alpha_d_CC_y5=_b[d_CC]
scalar alpha_log_income_y1_2=_b[log_income_y1_2]
scalar alpha_hours_y1_2=_b[hours_y1_2]


*Contributions
foreach variable of varlist tq17a log_income_y3_5 hours_y3_5 log_income_y1_2 hours_y1_2{
	qui xi: reg `variable' i.p_assign
	scalar delta_`variable'_y5=_b[_Ip_assign_2]
	scalar cont_`variable'_y5=_b[_Ip_assign_2]*alpha_`variable'
}
scalar cont_d_CC_y5=delta_d_CC*alpha_d_CC_y5


*This is ATE
display ate_y5

*These are the contributions 
display b_tau_y5 
display cont_tq17a_y5 
display cont_d_CC_y5 
display cont_log_income_y3_5_y5 
display cont_hours_y3_5_y5
display cont_log_income_y1_2_y5
display cont_hours_y1_2_y5

*In % terms: not using these
foreach variable in b_tau_y5 cont_tq17a_y5 cont_d_CC_y5 cont_log_income_y3_5_y5 cont_hours_y3_5_y5 cont_log_income_y1_2_y5 cont_hours_y1_2_y5{
	scalar `variable'_pp=`variable'*100/ate_y5
}

display b_tau_y5_pp
display cont_tq17a_y5_pp 
display cont_d_CC_y5_pp
display cont_log_income_y3_5_y5_pp 
display cont_hours_y3_5_y5_pp
display cont_log_income_y1_2_y5_pp 
display cont_hours_y1_2_y5_pp


*******************************************************************************************************************
**********************************YEAR-8 REGRESSION****************************************************************
*******************************************************************************************************************

*ATE
qui xi: reg etsq13a i.p_assign if d_y8==1
scalar ate_y8=_b[_Ip_assign_2]

*Regression: can't do fixed effects b/c there is no variation in random assignment within family.
xi: reg etsq13a t2q17a i.p_assign log_income_y6_8 hours_y6_8 /* Current inputs
*/ d_CC  log_income_y3_5 hours_y3_5  log_income_y1_2 hours_y1_2 /* Past inputs
*/ age_ra i.zboy i.ethnic i.marital i.cat_educ agechild  if d_y8==1/*X's*/



*saving coeff
scalar n_y8=e(N)
scalar b_tau_y8=_b[_Ip_assign_2]
scalar alpha_t2q17a=_b[t2q17a]
scalar alpha_log_income_y6_8=_b[log_income_y6_8]
scalar alpha_hours_y6_8=_b[hours_y6_8]
scalar alpha_log_income_y3_5=_b[log_income_y3_5]
scalar alpha_hours_y3_5=_b[hours_y3_5]
scalar alpha_d_CC_y8=_b[d_CC]
scalar alpha_log_income_y1_2=_b[log_income_y1_2]
scalar alpha_hours_y1_2=_b[hours_y1_2]


*Contributions
foreach variable of varlist t2q17a log_income_y6_8 hours_y6_8 log_income_y3_5 hours_y3_5 log_income_y1_2 hours_y1_2{
	qui xi: reg `variable' i.p_assign
	scalar delta_`variable'_y8=_b[_Ip_assign_2]
	scalar cont_`variable'_y8=_b[_Ip_assign_2]*alpha_`variable'
}
scalar cont_d_CC_y8=delta_d_CC*alpha_d_CC_y8


*This is ATE
display ate_y8

*These are the contributions
display b_tau_y8 
display cont_t2q17a_y8
display cont_d_CC_y8 
display cont_log_income_y6_8_y8 
display cont_hours_y6_8_y8
display cont_log_income_y3_5_y8 
display cont_hours_y3_5_y8
display cont_log_income_y1_2_y8
display cont_hours_y1_2_y8

*In % terms: not using these
foreach variable in b_tau_y8 cont_t2q17a_y8 cont_d_CC_y8 cont_log_income_y6_8_y8 cont_hours_y6_8_y8 cont_log_income_y3_5_y8 cont_hours_y3_5_y8 /*
*/ cont_log_income_y1_2_y8 cont_hours_y1_2_y8{
	scalar `variable'_pp=`variable'*100/ate_y8
}

display b_tau_y8_pp
display cont_t2q17a_y8_pp 
display cont_d_CC_y8_pp
display cont_log_income_y6_8_y8_pp 
display cont_hours_y6_8_y8_pp
display cont_log_income_y3_5_y8_pp 
display cont_hours_y3_5_y8_pp
display cont_log_income_y1_2_y8_pp 
display cont_hours_y1_2_y8_pp


*********The table**************************

*The matrix:
mat A_y2=(cont_d_CC\0\cont_log_income_y1_2\0\cont_hours_y1_2\0\b_tau\0\1\0\ate\0\n_y2)

mat A_y5=(cont_d_CC_y5\0\cont_log_income_y1_2_y5\0\cont_hours_y1_2_y5\0\b_tau_y5\0\cont_tq17a_y5\0\ate_y5\0\n_y5)

mat A_y8=(cont_d_CC_y8\0\cont_log_income_y1_2_y8\0\cont_hours_y1_2_y8\0\b_tau_y8\0\cont_t2q17a_y8\0\ate_y8\0\n_y8)


mat A=A_y2,A_y5,A_y8

*Saving in excel
putexcel C4=matrix(A) using "$results/Mediation/med_table_tquality", sheet("data") modify
