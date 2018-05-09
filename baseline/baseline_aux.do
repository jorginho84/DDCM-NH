
/*
This do-file constructs baseline summary statistics.
This is an input in baseline.do

*/

keep p_assign p_radatr p_bdatey p_bdatem p_bdated b_bdater bifage p_bdatey p_bdatem gender ethnic marital degree/*
*/ pastern2 work_ft currwage higrade c1 piinvyy epiinvyy 

destring higrade degree, force replace

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

*Dummies
gen d_gender=gender==2
gen d_afric=ethnic==1
gen d_hisp=ethnic==2
gen d_others=ethnic==3 | ethnic==4
gen d_white=ethnic==5
gen d_never=marital==1
gen d_married_spouse=marital==2
gen d_married_sep=marital==3
gen d_sep=marital==4


forvalues x=1/6{
	gen d_earn_`x'=pastern2==`x'
	}


gen RA=1 if p_assign=="E"
replace RA=2 if p_assign=="C"
label define ra_lbl 1 "Treatment" 2 "Control"
label values RA ra_lbl

*The baseline table
local x=1

qui{
foreach variable of varlist age_ra d_gender d_afric d_hisp d_white d_others d_never d_married_spouse d_married_sep d_sep d_HS higrade /* 
*/ d_earn_1 d_earn_2 d_earn_3 d_earn_4 d_earn_5 d_earn_6{
	
	ttest `variable', by(RA)
	mat A=(r(mu_1),r(mu_2),r(mu_1)-r(mu_2)\r(sd_1), r(sd_2), 0)
	

	xi: reg `variable' i.RA, vce(`SE')
	mat variance=e(V)
	mat A[2,3]=variance[1,1]^0.5/*replace it with S.E.*/
	test _IRA_2=0
	mat b_aux=(r(p)\0)
	mat D=A,b_aux/*add p-value*/
	mat c_aux=(e(N)\0)
	mat D=D,c_aux/*add N*/

	if `x'==1{
		mat baseline=D
	}
	else{
		mat baseline=baseline\D
	}
	local x=`x'+1
}

}
