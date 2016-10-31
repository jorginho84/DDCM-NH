/*
This do-file estimates an ordered probit model on SSRS and then computes marginal effects
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
scalar drop _all
program drop _all
set seed 100
set maxvar 15000
set more off



use "$databases/Youth_original2.dta", clear

*labels
qui: do "$codes/data_youth.do"
keep  sampleid child p_assign zboy agechild  tq17a t2q17a etsq13a /*SSRS year 2, 5, and 8, respectively*/
egen child_id=group(sampleid child)


/*The X's*/
qui:{

destring sampleid, force replace
sort sampleid
tempfile data_aux3
save `data_aux3', replace


use "$databases/CFS_original.dta", clear
do "$codes/data_cfs.do"


keep p_assign sampleid p_radatr p_bdatey p_bdatem p_bdated b_bdater bifage p_bdatey p_bdatem gender ethnic marital higrade degree /*
*/pastern2 work_ft curremp currwage higrade c1 piinvyy epiinvyy 

*Employment at baseline
gen emp_baseline=1 if curremp=="Yes"
replace emp_baseline=0 if curremp=="No"

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
gen d_HS=degree==1 | degree==2
label define educ_lbl 1 "High school diploma or GED" 0 "Less..."

keep sampleid age_ra gender ethnic marital d_HS higrade degree curremp pastern2
sort sampleid

merge 1:m sampleid using `data_aux3'
keep if _merge==3
drop _merge



}


*Only this variable needs rounding
gen t2q17a_aux=round(t2q17a)
drop t2q17a
rename t2q17a_aux t2q17a

/*

*xi: oprobit tq17a i.p_assign , vce(robust)

*/

/*Bootstrapped estimates*/



********************************************************************************
********************************************************************************
program est_top30, rclass
	version 14
	args ssrs
	qui xi: oprobit `ssrs' i.p_assign agechild i.marital d_HS higrade i.ethnic age_ra i.pastern2, vce(robust)
	*Obtaining the prob of reporting student in the top 30% of the class
	forvalues x=4/5{
		qui margins, dydx(_Ip_assign_2) predict(outcome(`x'))
		mat cat`x'_aux=r(b)
		scalar cat`x'=cat`x'_aux[1,1]
	}
	
	return scalar margin_top30=cat5+cat4

	
end
********************************************************************************
********************************************************************************

*xi: oprobit tq17a i.p_assign agechild i.marital d_HS i.ethnic age_ra, vce(robust)
*margins, dydx(_Ip_assign_2) predict(outcome(4))

local reps=1000

/*Girls*/
preserve
keep if zboy==0
local x=1
foreach year of varlist tq17a t2q17a etsq13a {
	

	bootstrap beta_y2=r(margin_top30), seed(12) reps(`reps') cluster(child_id) idcluster(newid)/* 
	*/ :  est_top30 `year' 
	mat beta=e(b)
	mat variance=e(V)
	mat variance[1,1]=sqrt(variance[1,1])
	qui: test beta_y2=0
	mat pvalue=r(p)
	mat data=beta\variance\pvalue

	if `x'==1{
		local letter="B"
	}
	
	else if `x'==2 {
		local letter="C"
	}
	
	else{
		local letter="D"
	}
	
	putexcel `letter'2=matrix(data) using "$results/Skills/skills_ssrs_margins", sheet("data") modify
	
	local x=`x'+1

}
restore

/*Boys*/
preserve
keep if zboy==1
local x=1
foreach year of varlist tq17a t2q17a etsq13a {
	

	bootstrap beta_y2=r(margin_top30), seed(12) reps(`reps') cluster(child_id) idcluster(newid)/* 
	*/ :  est_top30 `year' if zboy==1
	mat beta=e(b)
	mat variance=e(V)
	mat variance[1,1]=sqrt(variance[1,1])
	qui: test beta_y2=0
	mat pvalue=r(p)
	mat data=beta\variance\pvalue

	if `x'==1{
		local letter="B"
	}
	
	else if `x'==2 {
		local letter="C"
	}
	
	else{
		local letter="D"
	}
	
	putexcel `letter'5=matrix(data) using "$results/Skills/skills_ssrs_margins", sheet("data") modify
	
	local x=`x'+1

}
restore

/*Overall*/
local x=1
foreach year of varlist tq17a t2q17a etsq13a {
	

	bootstrap beta_y2=r(margin_top30), seed(12) reps(`reps') cluster(child_id) idcluster(newid)/* 
	*/ :  est_top30 `year'
	mat beta=e(b)
	mat variance=e(V)
	mat variance[1,1]=sqrt(variance[1,1])
	qui: test beta_y2=0
	mat pvalue=r(p)
	mat data=beta\variance\pvalue

	if `x'==1{
		local letter="B"
	}
	
	else if `x'==2 {
		local letter="C"
	}
	
	else{
		local letter="D"
	}
	
	putexcel `letter'14=matrix(data) using "$results/Skills/skills_ssrs_margins", sheet("data") modify
	
	local x=`x'+1

}

*********************************************************************************
*********************************************************************************

/* By employmemt status at baseline*/

*********************************************************************************
*********************************************************************************

gen emp_baseline=curremp=="Yes"
replace emp_baseline=. if curremp==" "


/*Employed at baseline*/
preserve
keep if emp_baseline==1


local x=1
foreach year of varlist tq17a t2q17a etsq13a {
	

	bootstrap beta_y2=r(margin_top30), seed(12) reps(`reps') cluster(child_id) idcluster(newid)/* 
	*/ :  est_top30 `year'
	mat beta=e(b)
	mat variance=e(V)
	mat variance[1,1]=sqrt(variance[1,1])
	qui: test beta_y2=0
	mat pvalue=r(p)
	mat data=beta\variance\pvalue

	if `x'==1{
		local letter="B"
	}
	
	else if `x'==2 {
		local letter="C"
	}
	
	else{
		local letter="D"
	}
	
	putexcel `letter'8=matrix(data) using "$results/Skills/skills_ssrs_margins", sheet("data") modify
	
	local x=`x'+1

}

restore


/*Employed at baseline*/
preserve
keep if emp_baseline==0


local x=1
foreach year of varlist tq17a t2q17a etsq13a {
	

	bootstrap beta_y2=r(margin_top30), seed(12) reps(`reps') cluster(child_id) idcluster(newid)/* 
	*/ :  est_top30 `year'
	mat beta=e(b)
	mat variance=e(V)
	mat variance[1,1]=sqrt(variance[1,1])
	qui: test beta_y2=0
	mat pvalue=r(p)
	mat data=beta\variance\pvalue

	if `x'==1{
		local letter="B"
	}
	
	else if `x'==2 {
		local letter="C"
	}
	
	else{
		local letter="D"
	}
	
	putexcel `letter'11=matrix(data) using "$results/Skills/skills_ssrs_margins", sheet("data") modify
	
	local x=`x'+1

}

restore

*xi: oprobit tq17a i.p_assign  if emp_baseline==1, vce(robust)


/*Baseline*/
tab tq17a if p_assign=="C" & zboy==1

tab t2q17a if p_assign=="C" & zboy==1

tab etsq13a if p_assign=="C" & zboy==1

 
