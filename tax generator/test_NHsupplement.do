/*
This do-file takes wage data from New Hope, simulates the NH supplement using TAXSIM, and compares it with actual information on NH supplements

*/


global results "C:\Users\Jorge\Dropbox\Chicago\Research\Human capital and the household\results\Taxes"


clear
clear matrix
clear mata
set more off


use "C:\Users\Jorge\Dropbox\Chicago\Research\Human capital and the household\results\taxdata.dta", clear

*Choose year
local year=1997

*Parameters
if `year'==1995{
	local barE_extra=300

}

else if `year'==1996{
	local barE_extra=1200

}

else if `year'==1997{
	local barE_extra=2100

}




***********************************************************************************************
/* Generating EITC disposable income*/
***********************************************************************************************


*Year
gen year=`year'

*N children (not accounting for child tax credit)
gen depx=nkids_year2
					
*Wisconsin
gen state=50

*Assume everyone is single
gen mstat=2 if married_year2==1
replace mstat=3 if married_year2==0 /*single with children*/

*Earnings
replace spouse_1995=0 if spouse_1995==.
gen pwages=earnings_`year' if married_year2==0
replace pwages=earnings_`year'+spouse_1995 if married_year2==1

*Simulating taxes
taxsim9,replace full

*EITC
rename v25 EITC_fed
rename v39 EITC_state

gen EITC=EITC_fed + EITC_state

*Disposable income: only from EITC
gen dincome_eitc=pwages+EITC


***********************************************************************************************
/* Generating NH disposable income for treated group*/
***********************************************************************************************

**************************************
*The wage subsidy: depends on individual's earnings
**************************************

gen Wsubsidy=.
replace Wsubsidy=0.25*earnings_`year' if earnings_`year'<=8500
replace Wsubsidy=3825-0.2*earnings_`year' if earnings_`year'>8500
replace Wsubsidy=0 if Wsubsidy<0 /*no taxes in NH*/

******************************
*The child allowance: It varies by number of children, household composition, and year
*depends on family earnings (pwages)
******************************
gen fam_size`year'=1+nkids_year2+married_year2

*initial per-child allowance
gen xstar=1700-100*nkids_year2 if nkids_year2<=4
replace xstar=1300 if nkids_year2>4


*fade-out earnings level
gen barE=30000 if fam_size`year'<4
replace barE=30000+`barE_extra' if fam_size`year'>=4
	
gen Beta=xstar/(8500-barE)
gen Alpha=xstar-Beta*8500
	
gen childa=. /*per-child subsidy*/
replace childa= xstar if pwages<=8500
replace childa=Alpha+Beta*pwages if pwages>8500
	
*total child allowance=per-child * number of children
gen total_childa=childa*nkids_year2
replace total_childa=0 if total_childa<0 /*no taxes in NH*/


******************************
*Disposable income NH: considering full-time requirement
******************************
gen dincome_NH=earnings_`year'+(Wsubsidy+total_childa)*fulltime`year'

gen dincome_NH_all=earnings_`year'+(Wsubsidy+total_childa)
	


***********************************************************************************************
/* Analysis*/
***********************************************************************************************
gen nh_subsidies=Wsubsidy+total_childa
twoway (scatter nh_subsidies earnings_`year' if nkids_year2==2)

*This picture looks like the one in the paper. Means that TAXSIM is working
twoway (scatter dincome_NH_all pwages if nkids_year2==1 & mstat==3 & pwages<25000)  (scatter dincome_eitc pwages if nkids_year2==1 & mstat==3 & pwages<25000)

twoway (scatter dincome_eitc pwages if nkids_year2==1 & married_year2==0)

twoway (scatter dincome_eitc pwages if nkids_year2==1 & married_year2==0)

gen dincome_eitc_fed=pwages+EITC_fed


twoway (scatter dincome_eitc_fed pwages if nkids_year2==1 & married_year2==0)

*Nonetheless, the levels do not coincide b/c my simulation assumes everyone works full time
gen supplement_`year'_sim=dincome_NH_all-dincome_eitc
replace supplement_`year'_sim=0 if supplement_`year'_sim<0
replace supplement_`year'_sim=0 if p_assign=="C"

sum supplement_`year'* if p_assign=="E" & fulltime`year'!=.

*Weighted supplement
gen supp_work=supplement_`year'_sim*fulltime`year'

*Conditional on receiving the supplement: weighted supplement equals 127. VERY CLOSE to the 126 that appears in the report!
sum supp_work  if supp_work>0
sum supplement_`year'_sim if supplement_`year'_sim>0, d
sum supplement_`year' if supplement_`year'>0 & p_assign=="E"


gen supp_workM=supp_work/12
ttest supp_workM=126 if supp_work>0

