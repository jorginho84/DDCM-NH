/*
Computing mean of AFDC and Food stamps (for model)

*/


global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"


clear
clear matrix
clear mata
set more off
set maxvar 15000

*Use the CFS study
use "$databases/CFS_original.dta", clear
qui: do "$codes/data_cfs.do"

preserve
keep sampleid wwq*
drop wwq33 wwq34 wwq35 wwq36 wwq37
reshape long wwq, i(sampleid) j(quarter)
sum wwq if wwq>0
restore

keep sampleid fsq*
drop fsq33 fsq34 fsq35  fsq36 fsq37
reshape long fsq, i(sampleid) j(quarter)
sum fsq if fsq>0

