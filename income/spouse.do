/*
This do-file computes spouse income

*/

global databases "/home/jrodriguez/NH-secure"
global codes "/home/jrodriguez/NH_HC/codes"
global results "/home/jrodriguez/NH_HC/results/income"



clear
clear matrix
clear mata
scalar drop _all
set more off
set maxvar 15000



*Use the CFS study
use "$databases/CFS_original.dta", clear
qui: do "$codes/data_cfs.do"

keep sampleid p_assign p_radatr cstartm curremp /*
*/rpa* spa* pta* moa* faa* f1a* c1a* c2a* c3a* c4a* c5a* c6a* c7a* c8a* o1a* o2a* o3a* o4a* s1a* s2a* s3a* s4a* s5a* /* 
*/r1a* r2a* r3a* r4a* r5a* r6a* r7a* r8a* n1a* n2a* n3a* n4a* n5a* n6a* /*income from different sources (year 2)
*/ p_assign sampleid p_radatr p_bdatey p_bdatem p_bdated b_bdater bifage p_bdatey p_bdatem gender ethnic marital higrade degree /*
*/pastern2 work_ft curremp currwage c1 piinvyy epiinvyy 

qui: destring cstartm rpa* spa* pta* moa* faa* f1a* c1a* c2a* c3a* c4a* c5a* c6a* c7a* c8a* o1a* o2a* o3a* o4a* s1a* s2a* s3a* s4a* s5a* /* 
*/r1a* r2a* r3a* r4a* r5a* r6a* r7a* r8a* n1a* n2a* n3a* n4a* n5a* n6a*, replace force 

*Indicates if responded the survey
gen d_survey=cstartm!=.


egen total_income_year2=rowtotal(rpa* spa* pta* moa* faa* f1a* c1a* c2a* c3a* c4a* c5a* c6a* c7a* c8a* o1a* o2a* o3a* o4a* s1a* s2a* s3a* s4a* s5a* /* 
*/r1a* r2a* r3a* r4a* r5a* r6a* r7a* r8a* n1a* n2a* n3a* n4a* n5a* n6a*)

*Income from the primary earner: paid work, AFDC, and Food Stamps
egen income_primary=rowtotal(rpapwlf1 rpawslf1 rpafslf1 rpaaflf1)
replace income_primary=0 if income_primary==.

*Income from spose: paid work, AFDC, and Food Stamps
egen income_spouse=rowtotal(spapwlf1 spawslf1 spafslf1 spaaflf1)
replace income_spouse=0 if income_spouse==.
gen lincome_spouse = log(income_spouse)

*Compare primary income and total income (year 2)
gen primary_total=income_primary/total_income_year2
sum primary_total

*spuse earnings
sum spapwlf1
sum rpapwlf1 if rpapwlf1>0

gen d_HS=degree==1 | degree==2


reg rpapwlf1 spapwlf1 d_HS

reg income_spouse rpapwlf1 d_HS
