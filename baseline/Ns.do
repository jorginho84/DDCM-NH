/*
This do-file counts the number of observations across CFS sub-samples

*/



global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Baseline"

clear
clear matrix
clear mata
set maxvar 15000

***************************
********ADULTS*************
***************************

/*CFS sample*/
use "$databases/CFS_original.dta", clear
qui: do "$codes/data_cfs.do"

*Eliminating 50 adults with no children
qui: do "$codes/baseline/drop_50.do"

file open loglog using "$results/N.tex", write replace
file write loglog "\begin{tabular}{lcccccc}" _n
file write loglog "\hline" _n
file write loglog "Data &       & \multicolumn{1}{c}{Treatment} &       & \multicolumn{1}{c}{Control} &       & \multicolumn{1}{c}{Total} \bigstrut\\" _n
file write loglog "\cline{1-1}\cline{3-7}      &       &       &       &       &       &  \bigstrut[t]\\" _n
file write loglog "A. Adults &       &       &       &       &       &  \\" _n

count if p_assign=="E"
local n_t = r(N)
count if p_assign=="C"
local n_c = r(N)
count
local nn = r(N)

file write loglog "CFS   &       & `n_t'    &       & `n_c'    &       & `nn' \\" _n

/*Estimation sample*/
use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear
duplicates drop sampleid, force

count if p_assign=="E"
local n_t = r(N)
count if p_assign=="C"
local n_c = r(N)
count
local nn = r(N)

file write loglog "Estimation   &       & `n_t'    &       & `n_c'    &       & `nn' \\" _n


/*Estimation sample + young children*/
use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear
gen age_t2 = age_t0 + 2
keep if age_t2<=6
duplicates drop sampleid, force
count if p_assign=="E"
local n_t = r(N)
count if p_assign=="C"
local n_c = r(N)
count
local nn = r(N)

file write loglog "With young children  &       & `n_t'    &       & `n_c'    &       & `nn' \\" _n
file write loglog "      &       &       &       &       &       &  \\" _n



******************************
********CHILDREN**************
******************************
clear

file write loglog "B. Children &       &       &       &       &       &  \\" _n



/*CFS*/
use "$databases/Youth_original2.dta", clear
qui: do "$codes/data_youth.do"

count if p_assign=="E"
local n_t = r(N)
count if p_assign=="C"
local n_c = r(N)
count
local nn = r(N)

file write loglog "CFS  &       & `n_t'    &       & `n_c'    &       & `nn' \\" _n

/*Estimation*/
use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear

count if p_assign=="E"
local n_t = r(N)
count if p_assign=="C"
local n_c = r(N)
count
local nn = r(N)

file write loglog "Estimation   &       & `n_t'    &       & `n_c'    &       & `nn' \\" _n

/*Estimation sample + young children*/
use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear
gen age_t2 = age_t0 + 2
keep if age_t2<=6

count if p_assign=="E"
local n_t = r(N)
count if p_assign=="C"
local n_c = r(N)
count
local nn = r(N)

file write loglog "Young children  &       & `n_t'    &       & `n_c'    &       & `nn' \\" _n
file write loglog "\hline" _n
file write loglog "\end{tabular}%" _n
file close loglog

