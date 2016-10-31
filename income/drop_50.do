/*
This do-file eliminates 50 adults from the CFS data that have no children in
the youh database
*/


*Eliminating 50 adults with no children
sort sampleid
tempfile data_cfs
save `data_cfs', replace

use "$databases/Youth_original2.dta", clear
keep sampleid
destring sampleid, force replace
gen child_indicator=1


merge m:1 sampleid using `data_cfs'
keep if _merge==3
drop _merge
duplicates drop sampleid, force
