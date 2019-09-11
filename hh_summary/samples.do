/*
This do-file computes Ns for each sample.

*/

global databases "/home/jrodriguez/NH-secure"
global codes "/home/jrodriguez/NH_HC/codes"
global results "/home/jrodriguez/NH_HC/results/model_v2"


use "$databases/Youth_original2.dta", clear

*labels
qui: do "$codes/data_youth.do"
keep  sampleid child p_assign zboy agechild p_assign p_radaym sdkidbd



*Age at baseline
destring sdkidbd, force replace
format sdkidbd %td
gen year_birth=yofd(sdkidbd)

*child age at baseline
gen year_ra = substr(string(p_radaym),1,2)
destring year_ra, force replace
replace year_ra = 1900 + year_ra

gen age_t0=  year_ra - year_birth

*due to rounding errors, ages 0 and 11 are 1 and 10
replace age_t0=1 if age_t0==0
replace age_t0=10 if age_t0==11
drop if age_t0 < 1 | age_t0 > 11


keep age_t0 sampleid child p_assign sdkidbd
reshape wide age_t0 sdkidbd, i(sampleid) j(child)

tempfile child_aux
save `child_aux', replace


*Merge data with adults and drop those who do not merge
use "$databases/CFS_original.dta", clear
qui: do "$codes/data_cfs.do"

qui: count
local n_cfs = r(N)

merge 1:1 sampleid using `child_aux'
keep if _merge == 3
drop _merge

qui: count
local n_cfs2 = r(N)

keep if gender == 2

qui: count
local n_reduced = r(N)

reshape long age_t0 sdkidbd, i(sampleid) j(child)
qui: count
local n_children1 = r(N)

sort sampleid sdkidbd

bysort sampleid: egen seq_aux = seq()
replace seq_aux = - seq_aux

sort sampleid seq_aux

bysort sampleid: egen seq_aux_2 = seq()

keep if seq_aux_2 == 1
drop seq_aux* sdkidbd

qui: count
local n_children2 = r(N)

qui: do "$codes/model_v2/sample_model.do"
qui: count
local n_children3 = r(N)


qui: count if age_t0<=4
local n_children4 = r(N)


*This is original N
display `n_cfs'

*This is the original CFS without adults/children without merge
display `n_cfs2'

*This is the original only-women sample
display `n_reduced'

*This is sample of reduced-form children
display `n_children1'


*This is sample of reduced-form children (young)
display `n_children1_young'


*This is sample of younger children per-family (equal to number of adults reduced)
display `n_children2'

*This is the estimation sample
display `n_children3'

*This is the counterfactual sample, young kids
display `n_children4'





