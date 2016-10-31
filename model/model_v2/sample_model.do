/*
This do-file saves a database of control variables and choices.
The sample is used to estimate the structural model.
Earnings=UI +CSJs. Annual earnings
Hours=Survey. Year-2: includes CSJs. Weekly hours


Recovers EITC disposable income from income.do

run data_income.do first

*/


global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model"


clear
clear matrix
clear mata
scalar drop _all
set more off
set maxvar 15000


*Use the CFS study
use "$databases/CFS_original.dta", clear
qui: do "$codes/data_cfs.do"


***************************************************************************************
/*
Recovering control variables
*/
***************************************************************************************

qui: do "$codes/model/wage_process/Xs.do"



/*
*ethnic dummies (baseline: black)
forvalues x=2/5{
	gen d_ethnic_`x'=ethnic==`x'
}

*do not consider d_ethnic_3: no observations
drop d_ethnic_3
*/

*marital status dummies at baseline
forvalues x=2/4{
	gen d_marital_`x'=marital==`x'
}

*Marital status at baseline
gen married_y0=marital==2

*Marital status: 1 if with spouse/partner and 0 otherwise
gen married_year2=0
replace married_year2=1 if c54=="2"
replace married_year2=1 if c55=="1"
replace married_year2=. if c1==" " /*Not in survey*/


gen married_year5=0
replace married_year5=1 if piq94=="6"
replace married_year5=1 if piq95=="2"
replace married_year5=. if piinvyy==" " /*Not in survey*/


gen married_year8=0
replace married_year8=1 if epi75=="6"
replace married_year8=1 if epi76=="1"
replace married_year8=. if epiinvyy==" " /*Not in survey*/

*past earnings dummies
forvalues x=2/6{
	gen d_pastern_`x'=pastern2==`x'
}

*Gender dummy
gen d_women=gender==2

gen constant=1

gen age_ra2=age_ra^2


*Kids at baseline

destring kid*daty, force replace
gen nkids_baseline=0

forvalues x=1/7{

	replace nkids_baseline=nkids_baseline+1 if kid`x'daty!=.
}


gen d_RA=p_assign=="E"


destring c1 piinvyy epiinvyy, force replace
*Kids at year 2
gen nkids_year2=nkids_baseline
replace nkids_year2=nkids_year2+1 if c53d_1=="1"
replace nkids_year2=. if c1==. /*Not in survey*/
gen d_born_year2=c53d_1=="1"
replace d_born_year2=. if c1==.


*Kids at year 5
gen nkids_year5=nkids_year2
replace nkids_year5=nkids_year5+1 if piq93e=="2"
replace nkids_year5=. if piinvyy==. /*Not in survey*/
gen d_born_year5=piq93e=="2"
replace d_born_year5=. if piinvyy==.


*Kids at year 8
gen nkids_year8=nkids_year5
replace nkids_year8=nkids_year8+1 if epi74e=="1"
replace nkids_year8=. if epiinvyy==. /*Not in survey*/
gen d_born_year8=epi74e=="1"
replace d_born_year8=. if epiinvyy==.


keep sampleid d_RA age_ra age_ra2 d_marital* d_HS  nkids_baseline constant curremp higrade nkids* married*

*Expanding to children
tempfile data_temp
save `data_temp', replace
use "$databases/Youth_original2.dta", clear
keep sampleid child agechild
*keep if agechild<=7 & agechild>=5
destring sampleid, force replace
merge m:1 sampleid using `data_temp'
keep if _merge==3
drop _merge


sort sampleid child
tempfile data_control
save `data_control', replace

***************************************************************************************
/*
Recovering Child care and SSRS
*/
***************************************************************************************


use "$databases/Youth_original2.dta", clear
qui: do "$codes/data_youth.do"
keep sampleid child agechild/* identifiers
*/ c68* c69* c70* c73 /*CC use and payments (year 2)
*/ piq113da  piq114* piq119a piq128a piq128b/* CC use and payments (year 5)    
*/ tq17a tq17b tq17c tq17h /*skills t1
*/ t2q17a etsq13a /*skills t5 and t8*/
destring sampleid, force replace

*Age at baseline
gen age_t0=agechild-2
gen age_t02=age_t0^2

/*Local labels: use these in regressions*/
local CC_use c68* c69*


/*Number of months on each child care: t=1*/

gen CC_HS_months=c70a_1 if c69a_2==child
replace CC_HS_months=c70a_2 if c69a_4==child

gen CC_PS_months=c70b_1 if c69b_2==child
replace CC_PS_months=c70b_2 if c69b_4==child

gen CC_ED_months=c70c_1 if c69c_2==child
replace CC_ED_months=c70c_2 if c69c_4==child

gen CC_OT_months=c70d_1 if c69d_2==child
replace CC_OT_months=c70d_2 if c69d_2==child

gen CC_PR_months=c70e_1 if c69e_2==child
replace CC_PR_months=c70e_2 if c69e_4==child

gen CC_HH_months=c70f_1 if c69f_2==child
replace CC_HH_months=c70f_1 if c69f_4==child

*number of months in formal
egen months_formal=rowtotal(CC_HS_months CC_PS_months CC_ED_months CC_OT_months)
egen months_informal=rowtotal(CC_PR_months CC_HH_months)
replace months_formal=. if c68a==. /*didn't answer survey*/
replace months_informal=. if c68a==.

*Main child care arragenment
egen max_months_t1=rowmax(CC_HS_months CC_PS_months CC_ED_months CC_OT_months CC_PR_months CC_HH_months)
gen d_CC2_t1=1 if max_months_t1==CC_HS_months | max_months_t1==CC_PS_months | max_months_t1==CC_ED_months | max_months_t1==CC_OT_months
replace d_CC2_t1=0 if  max_months_t1==CC_PR_months | max_months_t1==CC_HH_months | c68g==0
replace d_CC2_t1=. if max_months_t1==.

*Number of months in child care at t=4
egen max_months_t4=rowmax(piq114aa  piq114ba piq114ca piq114da piq114ea piq114fa piq114ga)
gen d_CC2_t4=1 if max_months_t4==piq114da
replace d_CC2_t4=0 if  max_months_t4==piq114aa | max_months_t4==piq114ba | max_months_t4==piq114ca | max_months_t4==piq114ea | max_months_t4==piq114fa | max_months_t4==piq114ga
replace d_CC2_t4=. if max_months_t4==.


*Payments child care
* year 1
rename c73 cc_pay_t1
gen d_free=.
replace d_free=1 if cc_pay_t1==0
replace d_free=0 if cc_pay_t1>0 & cc_pay_t1!=.

*Year 4
rename piq128a cc_pay_t4 
replace cc_pay_t4=13 if piq128b==1
replace cc_pay_t4=38 if piq128b==2
replace cc_pay_t4=75 if piq128b==3
replace cc_pay_t4=125 if piq128b==4
replace cc_pay_t4=175 if piq128b==5
replace cc_pay_t4=200 if piq128b==6


/*Child development measures*/

*This one is not categorized

rename tq17b skills_m1_t2
rename tq17c skills_m2_t2
rename tq17h skills_m3_t2

gen t2q17a_aux=round(t2q17a)
drop t2q17a
rename t2q17a_aux t2q17a

rename tq17a skills_t2
rename t2q17a skills_t5
rename etsq13a skills_t8

keep sampleid child d_CC* skills_* age_t0 age_t02 cc_pay* d_free
sort sampleid child

merge 1:1 sampleid child using `data_control'
keep if _merge==3
drop _merge

sort sampleid child
tempfile cc_data
save `cc_data', replace


***************************************************************************************
***************************************************************************************
/*
Recovering Hours
*/
***************************************************************************************
***************************************************************************************


*Use the CFS study
use "$databases/CFS_original.dta", clear
qui: do "$codes/data_cfs.do"


*Dropping those with no children in youth database
count
qui: do "$codes/income/drop_50.do"
count

tempfile data1_aux
save `data1_aux', replace


***********************
/*
0-2nd year

generate two varibles: hours and hours_CSJ

*/
***********************

keep sampleid p_assign p_radatr c1/*
*/ pthwjbf1 /*Hours worked away home (CFS)
*/r*smof1 r*syrf1 r*atjf1 r*emof1 r*eyrf1 r*hwsf1 r*hwef1 r*csjf1/*Year 2 variables*/

*date of RA+2 \approx date of year-2 interview
replace p_radatr=19000000+ p_radatr
tostring p_radatr, force replace
gen date_ra=mofd(date(p_radatr,"YMD"))
gen year_ra=yofd(date(p_radatr,"YMD"))
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
	rename r`x'csjf1 csj`x'
}

*Reshaping by spell number (19)
reshape long start_month start_year still end_month end_year hours_start hours_end csj, i(sampleid) j(spell)
destring hours* still c1, replace force


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


*Month and year of each spell: hours doesn't consider 0s
forvalues y=1994/1998{
	forvalues mm=1/12{
	gen hours`y'm`mm'=hours_end if csj!="100" & (( start<=monthly("`y'm`mm'","YM") & end>=monthly("`y'm`mm'","YM") )  | /*
	*/( start<=monthly("`y'm`mm'","YM")  & still==1 & monthly("`y'm`mm'","YM")==date_survey ) )
	*replace  hours`y'm`mm'=0 if  hours`y'm`mm'==. & c1!=.
	replace hours`y'm`mm'=. if monthly("`y'm`mm'","YM")>date_survey
	
	gen hoursCSJ`y'm`mm'=hours_end if csj=="100" & (( start<=monthly("`y'm`mm'","YM") & end>=monthly("`y'm`mm'","YM") )  | /*
	*/( start<=monthly("`y'm`mm'","YM")  & still==1 & monthly("`y'm`mm'","YM")==date_survey ) )
	*replace  hoursCSJ`y'm`mm'=0 if  hoursCSJ`y'm`mm'==. & c1!=.
	replace hoursCSJ`y'm`mm'=. if monthly("`y'm`mm'","YM")>date_survey
	

	
	}

}


*Reshape long again for month/year
drop hours_start hours_end
reshape long hours hoursCSJ, i(sampleid spell) j(month_aux) string

*SD of hours (across periods)
*sum hours
*local sd_hours=r(sd)

*Collapse my month. I'm averaging not considering 0s. If there are no jobs in the month: missing
keep sampleid p_assign month_aux hours hoursCSJ date_ra year_ra
gen month=monthly(month_aux, "YM")
format month %tm
sort sampleid month
rename hours hours_aux
egen hours=rowtotal(hours_aux hoursCSJ)
replace hours=. if hours==0 
drop hoursCSJ
collapse (mean) hours (first) p_assign date_ra year_ra, by(sampleid month)

*Collapse by year: if month did not work: hours=0
gen year=yofd(dofm(month))
drop month
replace hours=0 if hours==.
sort sampleid year
collapse (mean) hours (first) p_assign date_ra year_ra, by(sampleid year)


*Years since RA
gen years_ra=year-year_ra



*Reshape again to wide
replace years_ra=years_ra+1 /*trick to reshape*/
keep hours sampleid years_ra p_assign
reshape wide hours , i(sampleid) j(years_ra)

*Back to the original name
drop hours0
forvalues x=1/5{
	local m=`x'-1
	rename hours`x' hours_t`m'
}

drop hours_t2 hours_t3 hours_t4



merge 1:1 sampleid using `data1_aux'
keep if _merge==3
drop _merge


***********************
/*
*YEARS 5 AND 8

Hours on current job/last job in 12 months.
Includes 0s


*worked last 12 months according to survey y5
*piq49, piq50: full time
*piq51,piq54: part-time
*piq55, piq56: self-employed

*/
******************
*worked last 12 months according to survey y5
destring piinvyy epiinvyy, force replace
destring piq49 piq50 piq51 piq54 piq55 piq56, replace force 
gen emp_y4= piq49==7 | piq50==4 | piq51==6 | piq54==3 | piq55==5 | piq56==2
replace emp_y4=. if  piinvyy==.

*worked last 12 months according to survey y8
destring epi33 epi34 epi35 epi37 epi38 epi39, force replace
gen emp_y7= epi33==7 | epi34==4 | epi35==6 | epi37==3 | epi38==5 | epi39==2
replace emp_y7=. if epiinvyy==.

*These are the hours variables (current or more recent job)
destring piq66 epi54, replace force
rename piq66 hours_t4
rename epi54 hours_t7

*0's those unemployed in the last 12 months. Hours most recent job last 12 months (or current)
replace hours_t4=0 if emp_y4==0
replace hours_t4=. if piinvyy==.

replace hours_t7=0 if emp_y7==0
replace hours_t7=. if epiinvyy==.


keep sampleid hours_t* p_assign c1 piinvyy epiinvyy 
destring c1, replace force	

replace hours_t0=. if c1==.
replace hours_t1=. if c1==.


*The following database contains children's information
sort sampleid
merge 1:m sampleid using `cc_data'
keep if _merge==3
drop _merge

tempfile data_hours
save `data_hours', replace


************************************************************
*Recover total income by year since RA from data_income.do
**************************************************************

use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Income/data_income.dta", clear
merge 1:m sampleid using `data_hours'
keep if _merge==3
drop _merge

*Note: total_income_y0 is actually one year behind!!

drop total_income_y0 gross_y0 gross_nominal_y0 grossv2_y0 employment_y0 /*
*/ fs_y0 afdc_y0
forvalues x=1/9{
	local z=`x'-1
	rename total_income_y`x' total_income_y`z'
	rename gross_y`x' gross_y`z'
	rename grossv2_y`x' grossv2_y`z'
	rename gross_nominal_y`x' gross_nominal_y`z'
	rename employment_y`x' employment_y`z'
	rename afdc_y`x' afdc_y`z'
	rename fs_y`x' fs_y`z'

}


*Ajunting hours worked: 0 if they didn't report earnings and we have positive hours worked
*Using grossv2_: includes CSJs payments from 1997 (W-2 work)

foreach x of numlist 0 1 4 7{
	replace hours_t`x'=0 if grossv2_y`x'==0 & hours_t`x'!=.
}



*Hours Dummies
local i=1
foreach x of numlist 0 1 4 7 {
	gen cat_t`x'=.
	replace cat_t`x'=1 if hours_t`x'==0
	replace cat_t`x'=2 if hours_t`x'>0 & hours_t`x'<=29
	replace cat_t`x'=3 if hours_t`x'>=30 & hours_t`x'!=.
	
	*create dummies
	qui: tab cat_t`x', gen(hours_t`x'_cat)
	
}


*Child care payments are divided by two if Child A and B are in a family
*To real numbers
duplicates tag sampleid, gen(dupli)
replace cc_pay_t1=cc_pay_t1*1.1653595/2 if dupli==1
replace cc_pay_t4=cc_pay_t4*1.0958820/2 if dupli==1


/*
This is how I'm deciding on hours categories NOT ANYMORE

xtile q_h=hours_t0, nq(3)
table q_h, c(min hours_t0 max hours_t0 med hours_t0 mean hours_t0)
*/

****************************************************************

gen emp_baseline=1 if curremp=="Yes"
replace emp_baseline=0 if curremp=="No"

*Varphi identification.
forvalues x=0/1{
	gen d_emp_t`x'=cat_t`x'==3 | cat_t`x'==2
	replace d_emp_t`x'=. if  cat_t`x'==.
}

gen delta_emp=d_emp_t1-d_emp_t0

**Using d_HS based on highgrade: correlates more with wage
gen d_HS2=higrade>=12

keep sampleid child d_RA p_assign age_ra age_ra2 d_marital* d_HS d_HS2 nkids* hours_t* d_CC* constant emp_baseline  delta_emp skills_* c1 piinvyy /*
*/ epiinvyy total_income_y* married* cc_pay* gross_y* gross_nominal_y* grossv2_y* age_t0 age_t02 d_free afdc_y* fs_y*

save "$results/sample_model_theta_v2.dta", replace


*This is the sample to start the simulations
keep if c1!=. & piinvyy!=. & epiinvyy!=.


foreach x of varlist d_RA age_ra d_marital_2 d_HS2 nkids_baseline age_t0 {

	drop if `x'==.
}

*Maybe I can work with different samples???
save "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", replace
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.csv", comma  replace


