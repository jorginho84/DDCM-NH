/*
This auxiliary do-file recovers the X information from the adult database and merge it with the current database


*/


destring sampleid, force replace
***************************************************************************
/*The X's*/




sort sampleid
tempfile data_aux3
save `data_aux3', replace


use "$databases/CFS_original.dta", clear
do "$codes/data_cfs.do"


keep p_assign sampleid p_radatr p_bdatey p_bdatem p_bdated b_bdater bifage p_bdatey p_bdatem gender ethnic marital higrade degree /*
*/pastern2 work_ft curremp currwage c1 piinvyy epiinvyy p_radaym

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

gen d_HS2=higrade>=12

*emplyment st baseline
gen emp_baseline=curremp=="Yes"
replace emp_baseline=. if  curremp==" "

keep sampleid age_ra gender ethnic marital d_HS2 higrade /*
*/ pastern2 p_assign emp_baseline p_radaym
sort sampleid



merge 1:m sampleid using `data_aux3'
keep if _merge==3
drop _merge




***********************************************************
