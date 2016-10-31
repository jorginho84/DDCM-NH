/*

This do-file explores the impact of NEW HOPE on the educational expectations of children


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
keep  sampleid child tcsbs tcsis tcsis tcstot o97 o98 o99 o100 tacad tq11b p_assign zboy

destring o9* o100 tcs* tacad tq11b zboy, force replace

*Treatment status
gen RA=1 if p_assign=="E"
replace RA=2 if p_assign=="C"
label define ra_lbl 1 "Treatment" 2 "Control"
label values RA ra_lbl


*At least "mostly sure, etc", or more
forvalues x=97/100{
	forvalues y=1/4{
		gen o`x'_cat`y'=1 if o`x'<=`y' & o`x'>=1
		replace o`x'_cat`y'=0 if o`x'>`y' & o`x'<=5

	}
}

local nn=0
*Regressions and tables: overall, girls, and then boys.
foreach sex in "Overall" "Girls" "Boys"{

	preserve
	
	if `nn'==1{
		keep if zboy==0
	}
	else if `nn'==2{
		keep if zboy==1
	}


	local x=1
	foreach variable of varlist o97_cat1 o97_cat2 o97_cat3 o97_cat4 /*
	*/ o98_cat1 o98_cat2 o98_cat3 o98_cat4/*
	*/ o99_cat1 o99_cat2 o99_cat3 o99_cat4/*
	*/ o100_cat1 o100_cat2 o100_cat3 o100_cat4{ 
		
		ttest `variable', by(RA)
		mat A=(r(mu_1),r(mu_2),r(mu_1)-r(mu_2))
		
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
	putexcel B2=matrix(baseline) using "$results/expectations_Y2_Youth_`sex'", sheet("data") modify



	local number=2
	foreach x in "Go to high school: very sure"  "Go to high school: mostly sure or +" "Go to high school: somewhat sure or +" "Go to high school: not really sure or +"/*
	*/ "finish high school: very sure"  "finish high school: mostly sure or +" "finish high school: somewhat sure or +" "finish high school: not really sure or +"/*
	*/ "Go to college: very sure"  "Go to college: mostly sure or +" "Go to college: somewhat sure or +" "Go to college: not really sure or +"/*
	*/ "Finish college: very sure"  "Finish college: mostly sure or +" "Finish college: somewhat sure or +" "Finish college: not really sure or +"{
		
		putexcel A`number'=("`x'") using "$results/expectations_Y2_Youth_`sex'", sheet("data") modify
		local number=`number'+1
	}
	putexcel B1=("Treatment") using "$results/expectations_Y2_Youth_`sex'", sheet("data") modify
	putexcel C1=("Control") using "$results/expectations_Y2_Youth_`sex'", sheet("data") modify
	putexcel D1=("T-C") using "$results/expectations_Y2_Youth_`sex'", sheet("data") modify
	putexcel E1=("S.E.") using "$results/expectations_Y2_Youth_`sex'", sheet("data") modify
	putexcel F1=("p-value") using "$results/expectations_Y2_Youth_`sex'", sheet("data") modify
	
	local nn=`nn'+1
	restore

}
	
*******************************************************
/*Estimates from the adults database: year-2 results*/
*******************************************************

use "$databases/CFS_original.dta", clear

*labels
qui: do "$codes/data_cfs.do"



*Constructing databse of children
keep  sampleid p_assign p250 p251 

*only child-b children who answered p250 or p251
drop if p250==" " & p251==" "

rename p250 exp1
rename p251 exp2

gen child="B"

tempfile childb
save `childb', replace

use "$databases/CFS_original.dta", clear
do "$codes/data_cfs.do"

keep  sampleid p_assign p112 p113 
rename p112 exp1
rename p113 exp2
gen child="A"

append using `childb'

*Treatment status
gen RA=1 if p_assign=="E"
replace RA=2 if p_assign=="C"
label define ra_lbl 1 "Treatment" 2 "Control"
label values RA ra_lbl



destring  exp1 exp2, replace force

*At least "some college" or nothing
forvalues x=1/2{
	forvalues y=2/6{
		gen exp`x'_cat`y'=1 if exp`x'>=`y' & exp`x'<=6
		replace exp`x'_cat`y'=0 if exp`x'<`y' & exp`x'>=1

	}
}


*Regressions and tables
local x=1
foreach variable of varlist exp1_cat2 exp1_cat3 exp1_cat4 exp1_cat5 exp1_cat6/*
*/ exp2_cat2 exp2_cat3 exp2_cat4 exp2_cat5 exp2_cat6 {
	
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
putexcel B2=matrix(baseline) using "$results/expectations_Y2_Adult", sheet("data") modify



local number=2
*AT least finish highschool, at least...
foreach x in "How far would like: finish high school" "How far would like: technical school"  "How far would like: some college"/*
*/   "How far would like: finish college"  "How far would like: grad school"/*
*/ "How far will go: finish high school" "How far will go: technical school"  "How far will go: some college"/*
*/   "How far will go: finish college"  "How far will go: grad school"{
	putexcel A`number'=("`x'") using "$results/expectations_Y2_Adult", sheet("data") modify
	local number=`number'+1
}


putexcel B1=("Treatment") using "$results/expectations_Y2_Adult", sheet("data") modify
putexcel C1=("Control") using "$results/expectations_Y2_Adult", sheet("data") modify
putexcel D1=("T-C") using "$results/expectations_Y2_Adult", sheet("data") modify
putexcel E1=("S.E.") using "$results/expectations_Y2_Adult", sheet("data") modify
putexcel F1=("p-value") using "$results/expectations_Y2_Adult", sheet("data") modify

