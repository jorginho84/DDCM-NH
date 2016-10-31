/*
This do-file saves a dataset for testing whether my algorithm for generating supplements coincide with actual data on supplements

The test consists of:
1. generates simulated supplements using information from the data
2. generates annual observed supplements from observed monthly supplements
3. merge two series by sampleid and perform a t-test


1. inputs: by year(1995, 1996, 1997): family composition (number of children, if married or not), individual annual earnings, family earnings (individual +
2nd earners from spouse)

The two series may differ:
-Actual New Hope was delivered monthly. This means that reps had to infer what would annual earnings would look like. I have no information
into what method they end up using.
-There are some simplifications in the EITC forms.
-Data for hours worked is self-reported.


This do-file saves a databse containing:
sampleid, work income 1995/1997; spouse's earnings (surveys) 1995/1997; supplements 1995/1997; number of children 1995/1997, marital status 1995/1997

*Note:
I do not have on hours worked by week. This is necessary to compute the average hours per month requirement to receive the supplement. 
I only have hours worked for each job, and the month when the job started (but not the exact day). 
Hence, I have to assume that if the worker reports working 30 hours a week in a job in month X, 
I have to assume that those 30 hours were worked throughout the entire month


*/



global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"

clear
clear matrix
clear mata
set more off
set maxvar 15000

*Use the CFS study
use "$databases/CFS_original.dta", clear
do "$codes/data_cfs.do"

*Dropping those with no children in youth database
*count
*qui: do "$codes/income/drop_50.do"
*count

tempfile data1_aux
save `data1_aux', replace


****************************************
*Recovering hours worked
****************************************

keep sampleid p_assign p_radatr /*
*/ pthwjbf1 /*Hours worked away home (CFS)
*/r*smof1 r*syrf1 r*atjf1 r*emof1 r*eyrf1 r*hwsf1 r*hwef1 /*Year 2 variables*/

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


*Month and year of each spell: leaving missing were there are 0's
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
keep sampleid p_assign month_aux hours date_ra
gen month=monthly(month_aux, "YM")
format month %tm
collapse (mean) hours (first) p_assign date_ra, by(sampleid month)

*Transforming date to string
rename month month_aux
gen month_aux2=month(dofm(month_aux))
gen year_aux=year(dofm(month_aux))

gen month=""
forvalues y=1994/1998{
	forvalues m=1/12{
		replace month="`y'm`m'" if year_aux==`y' & month_aux2==`m'


	}

}

keep hours sampleid month p_assign
reshape wide hours, i(sampleid) j(month) string

*Merging with original
sort sampleid
merge 1:1 sampleid using `data1_aux'
drop _merge

*0's those unemployed
destring c1, force replace /*indicates survey2 respondant*/
foreach variable of varlist hours*{
	replace `variable'=0 if `variable'==.
	replace `variable'=. if c1==.
}


*Full-time work by month (dummy)

forvalues y=1994/1998{
	forvalues m=1/12{
		gen fulltime`y'm`m'=hours`y'm`m'>=30
		replace fulltime`y'm`m'=. if c1==.

	}



}

*Full-time proportion by year
forvalues y=1994/1998{
	egen fulltime`y'=rowmean(fulltime`y'm1 fulltime`y'm2 fulltime`y'm3 fulltime`y'm4 fulltime`y'm5 fulltime`y'm6 fulltime`y'm7 fulltime`y'm8 fulltime`y'm9 fulltime`y'm10 fulltime`y'm11 fulltime`y'm12 )
}


****************************************
*UI Earnings: quarters in calendar time
****************************************

*Renaming 
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

*Earnings: 1995/1996/1997.
egen earnings_1995=rowtotal(ern1995q1 ern1995q2 ern1995q3 ern1995q4)
egen earnings_1996=rowtotal(ern1996q1 ern1996q2 ern1996q3 ern1996q4)
egen earnings_1997=rowtotal(ern1997q1 ern1997q2 ern1997q3 ern1997q4)


*****************************************
*NH supplement: quarters in calendar time
*****************************************
destring sup*q*, replace force

*Renaming 
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

*Supplements: 1995/1996/1997
forvalues y=1995/1997{
	egen supplement_`y'=rowtotal(sup`y'q1 sup`y'q2 sup`y'q3 sup`y'q4 )

}

******************************************************
/*

Recovering spouse's earnings
Assume: constant for all years.

*/

******************************************************
qui: destring spapwlf1 ptapwlf1, replace force  /*from spouse and partner*/

*spouses's income: last month*12 of either spouse or partner
gen spouse_1995=spapwlf1*12
replace spouse_1995=ptapwlf1*12 if spapwlf1==.


*****************************************************
/*

Household composition

*Children at baseline

*marital status
year 2: c54 (2= married living with spouse) c55 (1=currently living with partner:)
year 5: piq94 (6= married living with spouse) piq95 (2=currently living with partner)
year 8: epi75 (6= married living with spouse) epi76 (1=currently living with partner)

*Numer of children living in the HH
kids at baseline: kid*daty, and then add 1 of in year x declares to had 
a child

*Approximate household size: spouse+children.


*/
****************************************************

*Kids at baseline

destring kid*daty, force replace
gen nkids_baseline=0

forvalues x=1/7{

	replace nkids_baseline=nkids_baseline+1 if kid`x'daty!=.
}


destring c1 piinvyy epiinvyy, force replace

*Kids at year 2
gen nkids_year2=nkids_baseline
replace nkids_year2=nkids_year2+1 if c53d_1=="1"
replace nkids_year2=. if c1==. /*Not in survey*/


*Kids at year 5
gen nkids_year5=nkids_year2
replace nkids_year5=nkids_year5+1 if piq93e=="2"
replace nkids_year5=. if piinvyy==. /*Not in survey*/

*Kids at year 8
gen nkids_year8=nkids_year5
replace nkids_year8=nkids_year8+1 if epi74e=="1"
replace nkids_year8=. if epiinvyy==. /*Not in survey*/


*Marital status: 1 if with spouse/partner and 0 otherwise
gen married_year2=0
replace married_year2=1 if c54=="2"
replace married_year2=1 if c55=="1"
replace married_year2=. if c1==. /*Not in survey*/


gen married_year5=0
replace married_year5=1 if piq94=="6"
replace married_year5=1 if piq95=="2"
replace married_year5=. if piinvyy==. /*Not in survey*/


gen married_year8=0
replace married_year8=1 if epi75=="6"
replace married_year8=1 if epi76=="1"
replace married_year8=. if epiinvyy==. /*Not in survey*/

*Approximate household size
gen hh_year2=married_year2+nkids_year2
gen hh_year5=married_year5+nkids_year5
gen hh_year8=married_year8+nkids_year8


*Saving database
keep sampleid p_assign earnings_1* supplement_* spouse_1995 nkids_year2 married_year2 /* 
*/ fulltime1994 fulltime1995 fulltime1996 fulltime1997 fulltime1998

saveold "$results/taxdata.dta", replace version(12)
