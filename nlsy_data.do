*set path for graphs and data
set more off
global data "C:\Users\Jorge\Documents\My Dropbox\Chicago\Papers\Pre_k\data\NLSY"

*****************************************************************
*****************************************************************
*NLSY*
*****************************************************************
*****************************************************************

clear
infile using "$data\nlsy3", using("$data\nlsy3.dat")
do "$data\nlsy3-value-labels.do"


rename R0000100 ID
rename R0214800 sex_parent
rename R0214700 race_parent

rename	R0217501	marital_status_1979
rename	R0405601	marital_status_1980
rename	R0618601	marital_status_1981
rename	R0898401	marital_status_1982
rename	R1144901	marital_status_1983
rename	R1520101	marital_status_1984
rename	R1890801	marital_status_1985
rename	R2257901	marital_status_1986
rename	R2445301	marital_status_1987
rename	R2871000	marital_status_1988
rename	R3074700	marital_status_1989
rename	R3401400	marital_status_1990
rename	R3656800	marital_status_1991
rename	R4007300	marital_status_1992
rename	R4418400	marital_status_1993
rename	R5081400	marital_status_1994
rename	R5166700	marital_status_1996
rename	R6479300	marital_status_1998
rename	R7007000	marital_status_2000
rename	R7704300	marital_status_2002
rename	R8496700	marital_status_2004
rename	T0988500	marital_status_2006
rename	T2210500	marital_status_2008
rename	T3108400	marital_status_2010
rename	T4112900	marital_status_2012

/*highest grade ever completed*/
rename	R0216701	educ_1979
rename	R0406401	educ_1980
rename	R0618901	educ_1981
rename	R0898201	educ_1982
rename	R1145001	educ_1983
rename	R1520201	educ_1984
rename	R1890901	educ_1985
rename	R2258001	educ_1986
rename	R2445401	educ_1987
rename	R2871101	educ_1988
rename	R3074801	educ_1989
rename	R3401501	educ_1990
rename	R3656901	educ_1991
rename	R4007401	educ_1992
rename	R4418501	educ_1993
rename	R5103900	educ_1994
rename	R5166901	educ_1996
rename	R6479600	educ_1998
rename	R7007300	educ_2000
rename	R7704600	educ_2002
rename	R8497000	educ_2004
rename	T0988800	educ_2006
rename	T2210700	educ_2008
rename	T3108600	educ_2010

/*family income*/

rename	R0217900	income_1979
rename	R0406010	income_1980
rename	R0618410	income_1981
rename	R0898600	income_1982
rename	R1144500	income_1983
rename	R1519700	income_1984
rename	R1890400	income_1985
rename	R2257500	income_1986
rename	R2444700	income_1987
rename	R2870200	income_1988
rename	R3074000	income_1989
rename	R3400700	income_1990
rename	R3656100	income_1991
rename	R4006600	income_1992
rename	R4417700	income_1993
rename	R5080700	income_1994
rename	R5166000	income_1996
rename	R6478700	income_1998
rename	R7006500	income_2000
rename	R7703700	income_2002
rename	R8496100	income_2004
rename	T0987800	income_2006
rename	T2210000	income_2008
rename	T3107800	income_2010
rename	T4112300	income_2012

/*Poverty status*/
rename	R0217910	poverty_1979
rename	R0406100 	poverty_1980
rename	R0618500 	poverty_1981
rename	R0898700 	poverty_1982
rename	R1144600  	poverty_1983
rename	R1519800 	poverty_1984
rename	R1890500	poverty_1985
rename	R2257600 	poverty_1986
rename	R2444900	poverty_1987
rename	R2870400 	poverty_1988
rename	R3074100	poverty_1989
rename	R3400800 	poverty_1990
rename	R3656200	poverty_1991
rename	R4006700 	poverty_1992
rename	R4417800 	poverty_1993
rename	R5080800 	poverty_1994
rename	R5166100 	poverty_1996
rename	R6478800 	poverty_1998
rename	R7006600	poverty_2000
rename	R7703900	poverty_2002
rename	R8496300 	poverty_2004
rename	T0987900 	poverty_2006
rename	T2210100	poverty_2008
rename	T3108000	poverty_2010
rename	T4112500 	poverty_2012



/*weekd worked last calendar year*/

rename	R0215700	weeks_1979
rename	R0407200	weeks_1980
rename	R0646300	weeks_1981
rename	R0896900	weeks_1982
rename	R1145300	weeks_1983
rename	R1520500	weeks_1984
rename	R1891200	weeks_1985
rename	R2258300	weeks_1986
rename	R2445700	weeks_1987
rename	R2871500	weeks_1988
rename	R3075200	weeks_1989
rename	R3401900	weeks_1990
rename	R3657300	weeks_1991
rename	R4007800	weeks_1992
rename	R4418900	weeks_1993
rename	R5081900	weeks_1994
rename	R5167200	weeks_1996
rename	R6480000	weeks_1998
rename	R7007700	weeks_2000
rename	R7705000	weeks_2002
rename	R8497400	weeks_2004
rename	T0989200	weeks_2006
rename	T2211000	weeks_2008
rename	T3108900	weeks_2010
rename	T4113400	weeks_2012

/*hours worked last calenday year*/

rename	R0215710	hrs_1979
rename	R0407300	hrs_1980
rename	R0646600	hrs_1981
rename	R0896800	hrs_1982
rename	R1145200	hrs_1983
rename	R1520400	hrs_1984
rename	R1891100	hrs_1985
rename	R2258200	hrs_1986
rename	R2445600	hrs_1987
rename	R2871400	hrs_1988
rename	R3075100	hrs_1989
rename	R3401800	hrs_1990
rename	R3657200	hrs_1991
rename	R4007700	hrs_1992
rename	R4418800	hrs_1993
rename	R5081800	hrs_1994
rename	R5167100	hrs_1996
rename	R6479900	hrs_1998
rename	R7007600	hrs_2000
rename	R7704900	hrs_2002
rename	R8497300	hrs_2004
rename	T0989100	hrs_2006
rename	T2210900	hrs_2008
rename	T3108800	hrs_2010
rename	T4113300	hrs_2012


/*hours=0 and weeks=0 for those who have valid skips*/
/*marital status: missings those who do not know*/
/*income: missing to those who do not know and refuse*/

forvalues y=1979/1994{
replace hrs_`y'=0 if hrs_`y'<0
replace weeks_`y'=0 if weeks_`y'<0
replace marital_status_`y'=. if marital_status_`y'<0
replace income_`y'=. if income_`y'<0
}
forvalues y=1996(2)2012{
replace hrs_`y'=0 if hrs_`y'<0
replace weeks_`y'=0 if weeks_`y'<0
replace marital_status_`y'=. if marital_status_`y'<0
replace income_`y'=. if income_`y'<0
}


/*highest grade reported*/

forvalues y=1979/1994{
replace educ_`y'=0 if educ_`y'>=93
}

forvalues y=1996(2)2010{
replace educ_`y'=0 if educ_`y'>=93
}


egen educ=rowmax(educ*)

*Schooling indicators
gen lessthanhs=(educ<=11)
gen hs=(educ==12)
gen somecoll=(educ>=13 & educ<=15)
gen college=(educ==16)
gen collplus=(educ>=17)

keep lessthanhs hs  somecoll college collplus educ hrs* weeks* marital* ID sex_parent race_parent income* poverty* ID


sort ID
tempfile nlsy
save `nlsy', replace


*****************************************************************
*****************************************************************
/*

NLSYC

The sample: 
(1) child ever attended child care vs does who do not
3-4 years old and declare enrollment in preeschool/nursery? (check in NLS investigator)

(2) head start versus nothing at ages 3-4 year olds.

*/
*****************************************************************
*****************************************************************


clear
infile using "$data\data_hs_nlsy", using("$data\data_hs_nlsy.dat")
do "$data\data_hs_nlsy-value-labels.do"

*mother's ID
rename C0000200 ID

*ever attended day care (92)
rename C1001300 daycare_ever92

*ever attended preeschool (92)
rename C1001200 PS_ever92

*ever attended HS (92)
rename C1001400 HS_ever92

*Age when first attended HS (92)
rename C1001500 age_HS_92

*How long attended HS (92)
rename C1001600 long_HS92

rename C0005700 DOB
rename C0005300 race
rename C0005400 sex
rename  C3601700 father_present2008

*Year of HS use
gen HS_year=DOB+age_HS_92 if age_HS_92>0
/*

*The sample: children that attended head start between 1987 and 1991 vs children below poverty line in the relevant period and
did not attend HS(DOB>=1983 & DOB<=1988). 
Poverty in years 87-91

*/
#delimit;
gen group=(HS_ever92==1 & (age_HS_92==3 | age_HS_92==4)  & (HS_year>=1987 & HS_year<=1991)) |  
(HS_ever92==0 & DOB>=1983 & DOB<=1988 );
#delimit cr

keep if group==1

keep group DOB HS* sex race ID
sort ID
merge m:1 ID using `nlsy'
*all children merged
keep if _merge==3 /*only children and mothers*/


/*marital status dynamics*/
forvalues y=1979/1994{
gen married_`y'=marital_status_`y'==1
gen divsep_`y'=marital_status_`y'==2 | marital_status_`y'==3
gen never_`y'=marital_status_`y'==0
}


forvalues y=1996(2)2012{
gen married_`y'=marital_status_`y'==1
gen divsep_`y'=marital_status_`y'==2 | marital_status_`y'==3
gen never_`y'=marital_status_`y'==0
}

*Only children living in poverty as control group
gen group2=(poverty_1987==1 & poverty_1988==1 & poverty_1989==1 & poverty_1990==1 & poverty_1991==1)

*Differences in marriage, controlling for education and family income

qui: reg married_1979 HS_ever92 hs  somecoll college collplus
lincom  _b[HS_ever92]
local married_hs_`y'=r(estimate)

*Marriage
*HS sample
forvalues y=1979/1994{
qui: reg married_`y' HS_ever92 hs  somecoll college collplus income_`y' if group2==1
qui: lincom  _b[HS_ever92]
local married_hs_`y'=r(estimate)
display `married_hs_`y''

}


forvalues y=1996(2)2012{
qui: reg married_`y' HS_ever92 hs  somecoll college collplus income_`y' if group2==1
qui: lincom  _b[HS_ever92]
local married_hs_`y'=r(estimate)
display `married_hs_`y''

}


*Divorce/separated
forvalues y=1979/1994{
qui: reg divsep_`y' HS_ever92 hs  somecoll college collplus income_`y' if group2==1
qui: lincom  _b[HS_ever92]
local divsep_hs_`y'=r(estimate)
display `divsep_hs_`y''

}


forvalues y=1996(2)2012{
qui: reg divsep_`y' HS_ever92 hs  somecoll college collplus income_`y' if group2==1
qui: lincom  _b[HS_ever92]
local divsep_hs_`y'=r(estimate)
display `divsep_hs_`y''

}




*Marriage
*HS sample
forvalues y=1979/1994{
qui: reg married_`y' HS_ever92 if group2==1
qui: lincom  _b[HS_ever92]
local married_hs_`y'=r(estimate)
display `married_hs_`y''

}


forvalues y=1996(2)2012{
qui: reg married_`y' HS_ever92 if group2==1
qui: lincom  _b[HS_ever92]
local married_hs_`y'=r(estimate)
display `married_hs_`y''

}


*Divorce/separated
forvalues y=1979/1994{
qui: reg divsep_`y' HS_ever92 if group2==1
qui: lincom  _b[HS_ever92]
local divsep_hs_`y'=r(estimate)
display `divsep_hs_`y''

}


forvalues y=1996(2)2012{
qui: reg divsep_`y' HS_ever92 if group2==1
qui: lincom  _b[HS_ever92]
local divsep_hs_`y'=r(estimate)
display `divsep_hs_`y''

}

