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
local scale = 1.3


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

keep sampleid p_assign p_radatr piinvyy/*
*/ pthwjbf1 /*Hours worked away home (CFS)
*/r*smof1 r*syrf1 r*atjf1 r*emof1 r*eyrf1 r*hwsf1 r*hwef1 /*Year 2 variables*/

*date of RA+2 \approx date of year-2 interview
replace p_radatr=19000000+ p_radatr
tostring p_radatr, force replace
gen date_ra=mofd(date(p_radatr,"YMD"))
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


*Month and year of each spell: leving missing on 0's
forvalues y=1994/1998{
	forvalues mm=1/12{
	gen hours`y'm`mm'=hours_end if ( start<=monthly("`y'm`mm'","YM") & end>=monthly("`y'm`mm'","YM") )  | /*
	*/( start<=monthly("`y'm`mm'","YM")  & still==1 & monthly("`y'm`mm'","YM")==date_survey )
	
	replace hours`y'm`mm'=0 if monthly("`y'm`mm'","YM")>date_survey
	}

}



*Reshape long again for month/year
drop hours_start hours_end
reshape long hours, i(sampleid spell) j(month_aux) string

*SD of hours (across periods)
*sum hours
*local sd_hours=r(sd)

*Collapse my month: and we are done!
keep sampleid p_assign month_aux hours date_ra
gen month=monthly(month_aux, "YM")
format month %tm




/*
*For each individual, average hours by month. 
*/
collapse (mean) hours (first) p_assign date_ra, by(sampleid month)

*Months since RA
gen months_ra=month-date_ra

*Now we count . and 0's
*replace hours=0 if hours==.


*Reshape again to build the graph using collapse
replace months_ra=months_ra+23 /*trick to reshape*/
keep hours sampleid months_ra p_assign
reshape wide hours, i(sampleid) j(months_ra)


*Obtaining control variables
if `controls'==1{

	do "$codes/income/Xs.do"
	local control_var age_ra i.marital i.ethnic d_HS higrade i.pastern2
	
}

	
*Dropping 50 observations with no children
do "$codes/time/drop_50.do"



*Don't have full sample here
drop hours0 hours1 hours2 hours3

*Matrix of p-values (the first 3 will not show up in the graph anyways)
forvalues x=4/47{
	*Including 0s
	replace hours`x'=0 if hours`x'==.
	qui xi: reg hours`x' i.p_assign `control_var', vce(`SE')
	qui: test _Ip_assign_2=0
		
	if `x'==4{
		mat pvalue=r(p)
	}
		
	else{
		mat pvalue=pvalue\r(p)
	}
		


}



*Average hours by levels
collapse (mean) hours*, by(p_assign)
reshape long hours, i(p_assign) j(month)
replace month=month-23 /*back to the original number*/

*Recovering matrix of pvalues (fake labels for figure)
gen p_assign_aux=1 if p_assign=="E"
replace p_assign_aux=2 if p_assign=="C"
sort p_assign_aux month
drop p_assign_aux
svmat pvalue

*After this month, there are no records
drop if month>24

*This is the pvalue label
gen label_aux=""
replace label_aux="*" if pvalue1<=0.1
replace label_aux="**" if pvalue1<=0.05
replace label_aux="***" if pvalue1<=0.01

gen mean_aux1=hours if p_assign=="E" & pvalue1<=0.01
gen mean_aux2=hours if p_assign=="E" & pvalue1<=0.05 &  pvalue1>0.01
gen mean_aux3=hours if p_assign=="E" & pvalue1<=0.1 &  pvalue1>0.05

*According to the LS_survey: full sample from -7 onwards.
*Before 0, I have data for individuals who where working
twoway (line hours month if p_assign=="E" & month>=0 ,  lpattern(solid) lwidth(thin) ) /*
*/ (scatter mean_aux1 month if p_assign=="E" & month>=0 ,  msymbol(circle) mcolor(blue) mfcolor(blue)) /*
*/ (scatter mean_aux2 month if p_assign=="E" & month>=0 ,  msymbol(circle) mcolor(blue) mfcolor(ltblue)) /*
*/ (scatter mean_aux3 month if p_assign=="E" & month>=0 ,  msymbol(circle) mcolor(blue) mfcolor(none)) /*
*/(line hours month if p_assign=="C" & month>=0,  lpattern(dash) lwidth(thin)),/*
*/scheme(s2mono) legend(order(1 "Treatment" 5 "Control")  )/*
*/ytitle(Hours worked (weekly)) xtitle(Months since RA)/*
*/graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))/*
*/xlabel(0(5)24) ylabel(, nogrid) scale(`scale')

graph save "$results/Time/hours_mra.gph", replace
graph export "$results/Time/hours_mra.pdf", as(pdf) replace

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

*Ra indicator
gen RA=1 if p_assign=="E"
replace RA=2 if p_assign=="C"
label define ra_lbl 1 "Treatment" 2 "Control"
label values RA ra_lbl

*Indicates year-x missing
gen d_year5=piinvdd==" "
gen d_year8=epiinvyy==" "


*****Employment variables*****
gen employment_year5=(piq49=="7" ) | (piq49=="1" & piq51=="6")
replace employment_year5=. if d_year5==1

gen employment_year8=(epi33=="7" ) | (epi33=="0" & epi35=="6")
replace employment_year8=. if d_year8==1


*Obtaining control variables
if `controls'==1{

	qui: do "$codes/income/Xs.do"
	local control_var age_ra i.marital i.ethnic d_HS higrade i.pastern2
	
}

*Replacing 0s
replace piq66=0 if piq66==. & d_year5==0
replace epi54=0 if epi54==. & d_year8==0

*Regressions and table
local j=7
local y=5
foreach variable of varlist piq66 epi54{


	*qui ttest `variable' if employment_year`y'==1, by(RA)
	qui ttest `variable', by(RA)
	mat A=(r(mu_1),r(mu_2),0\r(sd_1), r(sd_2), 0)

	 xi: reg `variable' i.RA `control_var' if employment_year`y'==1, vce(`SE')
	mat variance=e(V)
	mat A[2,3]=variance[1,1]^0.5/*replace it with S.E.*/
	mat A[1,3]=_b[_IRA_2]
	qui test _IRA_2=0
	mat b_aux=(r(p)\0)
	mat data=A,b_aux/*add p-value*/

	
	*The table
	putexcel C`j'=matrix(data) using "$results/Time/hours_years5_8", sheet("data") modify
	
	local j=`j'+2
	local y=`y'+3


}



}

