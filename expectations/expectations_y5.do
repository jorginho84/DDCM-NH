/*

This do-file explores the impact of NEW HOPE on the educational expectations of children (year 5)

-individuals' aspirations and expectations: yiq45a-c and yaq46c-yaq46d (about the future)
-parents' report on expectations: piq147 piq148
-teacher expectations: t2q11a t2q11b t2q11c 


*/



global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Expectations"

/*
robust SE for small samples. Set to hc3 for more conservatives. 

See Angrist and Pischke for more information
"robust" SE can be misleading when the sample size is small and there is no much heteroskedasticity.
*/
local SE="hc2"

set more off
clear
clear matrix
clear mata
set maxvar 15000


*******************************************************
/*Estimates from the youth database: year-2 results*/
*******************************************************

use "$databases/Youth_original2.dta", clear

*labels
do "$codes/data_youth.do"
keep  sampleid child zboy p_assign /* Identifiers
*/ yiq45a yiq45b yiq45c /* Individual's expectations
*/ t2q11a t2q11b t2q11c /* Teacher's expectations 
*/ piq147 piq148 /*Parents' expectations*/


/*Local labels: use them in regressions*/
local identifiers sampleid child zboy
local individual yiq45a yiq45b yiq45c
local teacher t2q11a t2q11b t2q11c
local parents piq147 piq148

destring `individual' `teacher' `parents' zboy, force replace

*Treatment status
gen RA=1 if p_assign=="E"
replace RA=2 if p_assign=="C"
label define ra_lbl 1 "Treatment" 2 "Control"
label values RA ra_lbl


*Defining individual and teacher expectations: at least "mostly sure, etc", or more
foreach variable of varlist `individual' `teacher'{
	local x=5
	forvalues y=1/4{
		gen `variable'_`y'=1 if `variable'>=`x' & `variable'<=5
		replace `variable'_`y'=0 if `variable'<`x' & `variable'>=1
		local x=`x'-1
	}
	
	
	
}

*Defining parents expectations: at least "some college, etc", or more

foreach variable of varlist `parents'{
	forvalues x=2/6{
		gen `variable'_`x'=1 if `variable'>=`x' & `variable'<=6
		replace `variable'_`x'=0 if `variable'<`x' & `variable'>=1
	}
}



local individual yiq45a_* yiq45b_* yiq45c_*
local teacher t2q11a_* t2q11b_* t2q11c_*
local parents piq147_* piq148_*


*Regressions and tables for individual and teacher reports: overall, girls, and then boys.
local nn=0
foreach sex in "Overall" "Girls" "Boys"{

	preserve
	
	if `nn'==1{
		keep if zboy==0
	}
	else if `nn'==2{
		keep if zboy==1
	}

	local x=1
	foreach variable of varlist `individual' `teacher'{
		
		ttest `variable', by(RA)
		mat A=(r(mu_1),r(mu_2),r(mu_1)-r(mu_2))
		mat list A

		xi: reg `variable' i.RA, vce(`SE')
		mat variance=e(V)
		mat a_aux=variance[1,1]^0.5
		mat C=A,a_aux
		test _IRA_2=0
		mat b_aux=r(p)
		mat D=C,b_aux

		if `x'==1{
			mat baseline=D
		}
		else{
			mat baseline=baseline\D
		}
		local x=`x'+1
	}


	*the table
	putexcel B2=matrix(baseline) using "$results/expectations_Youth_Y5_`sex'", sheet("data") modify
	local number=2
	foreach x in "Finish high school: Very sure (individual)"  "Finish high school: Mostly sure or + (individual)"/* Individual: HS
	*/ "Finish high school: Somewhat sure or +(individual)" "Finish high school: not really sure or + (individual)"/* Individual: HS
	*/ "Go to college: Very sure (individual)"  "Go to college: Mostly sure or + (individual)"/*Individual: go to college
	*/ "Go to college: Somewhat sure or +(individual)" "Go to college: not really sure or + (individual)"/* Individual: go to college
	*/"Finish college: Very sure (individual)"  "Finish college: Mostly sure or + (individual)"/* Individual: finish college
	*/ "Finish college: Somewhat sure or + (individual)" "Finish college: not really sure or + (individual)"/* Individual: finish college
	*//*
	*/ "Finish high school: Very sure (teacher)"  "Finish high school: Mostly sure or + (teacher)"/* Teacher: HS
	*/ "Finish high school: Somewhat sure or +(teacher)" "Finish high school: not really sure or + (teacher)"/* Teacher: HS
	*/ "Go to college: Very sure (teacher)"  "Go to college: Mostly sure or + (teacher)"/*Teacher: go to college
	*/ "Go to college: Somewhat sure or +(teacher)" "Go to college: not really sure or + (teacher)"/* Teacher: go to college
	*/"Finish college: Very sure (teacher)"  "Finish college: Mostly sure or + (teacher)"/* Teacher: finish college
	*/ "Finish college: Somewhat sure or + (teacher)" "Finish college: not really sure or + (teacher)" /* Teacher: finish college
	*/{
		putexcel A`number'=("`x'") using "$results/expectations_Youth_Y5_`sex'", sheet("data") modify
		local number=`number'+1
	}
	putexcel B1=("Treatment") using "$results/expectations_Youth_Y5_`sex'", sheet("data") modify
	putexcel C1=("Control") using "$results/expectations_Youth_Y5_`sex'", sheet("data") modify
	putexcel D1=("T-C") using "$results/expectations_Youth_Y5_`sex'", sheet("data") modify
	putexcel E1=("S.E.") using "$results/expectations_Youth_Y5_`sex'", sheet("data") modify
	putexcel F1=("p-value") using "$results/expectations_Youth_Y5_`sex'", sheet("data") modify

	
	local nn=`nn'+1
	
	restore


}



*Regressions and tables parents reports: overall, girls, and then boys.
local nn=0
foreach sex in "Overall" "Girls" "Boys"{

	preserve
	
	if `nn'==1{
		keep if zboy==0
	}
	else if `nn'==2{
		keep if zboy==1
	}

	local x=1
	foreach variable of varlist `parents'{
		
		ttest `variable', by(RA)
		mat A=(r(mu_1),r(mu_2),r(mu_1)-r(mu_2))
		mat list A

		xi: reg `variable' i.RA, vce(`SE')
		mat variance=e(V)
		mat a_aux=variance[1,1]^0.5
		mat C=A,a_aux
		test _IRA_2=0
		mat b_aux=r(p)
		mat D=C,b_aux

		if `x'==1{
			mat baseline=D
		}
		else{
			mat baseline=baseline\D
		}
		local x=`x'+1
	}


	*the table
	putexcel B2=matrix(baseline) using "$results/expectations_Adults_Y5_`sex'", sheet("data") modify
	local number=2
	foreach x in "How far would like: finish high school"  "How far would like: technical school" /* How far would like
	*/ "How far would like: some college" "How far would like: finish college" "How far would like: grad school"/* How far would like
	*/ "How far will go: finish high school"  "How far will go: technical school" /* How far will go
	*/ "How far will go: some college" "How far will go: finish college" "How far will go: grad school"/* How far will go
	*/{
		putexcel A`number'=("`x'") using "$results/expectations_Adults_Y5_`sex'", sheet("data") modify
		local number=`number'+1
	}
	putexcel B1=("Treatment") using "$results/expectations_Adults_Y5_`sex'", sheet("data") modify
	putexcel C1=("Control") using "$results/expectations_Adults_Y5_`sex'", sheet("data") modify
	putexcel D1=("T-C") using "$results/expectations_Adults_Y5_`sex'", sheet("data") modify
	putexcel E1=("S.E.") using "$results/expectations_Adults_Y5_`sex'", sheet("data") modify
	putexcel F1=("p-value") using "$results/expectations_Adults_Y5_`sex'", sheet("data") modify

	
	local nn=`nn'+1
	
	restore


}



*******************************************************
/*Estimates from the adults database: year-2 results*/
*******************************************************
/*

Note: the expectation variable in this case is in the youth database already
Moreover, the expectation variable is already merged for every child, unlike year 2 database
*/




set more on
