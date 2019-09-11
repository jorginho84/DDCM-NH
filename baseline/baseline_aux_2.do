
/*
This do-file constructs baseline summary statistics.
This is an input in baseline.do

*/



*Dummies
rename d_women d_gender
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
