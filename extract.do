/*
This do-file extracts the original data and save it in stata format

*/


clear
clear matrix
clear mata
set more off
set maxvar 2000

*The CFS database

import delimited using "/home/icomercial/Jorge/NH-secure/14797066/ICPSR_30282/DS0002/30282-0002-Data-REST.tsv"
save "/home/icomercial/Jorge/NH-secure/CFS_original.dta", replace

clear
import delimited using "/home/icomercial/Jorge/NH-secure/14797066/ICPSR_30282/DS0001/30282-0001-Data-REST.tsv"
save "/home/icomercial/Jorge/NH-secure/Adults_original.dta", replace

clear
import delimited using "/home/icomercial/Jorge/NH-secure/14797066/ICPSR_30282/DS0003/30282-0003-Data-REST.tsv"
save "/home/icomercial/Jorge/NH-secure/Youth_original.dta", replace

/*
*Youth_original is corrupted. Use this one
use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/13347814/ICPSR_30282/DS0003/da30282-0003_REST", clear
*the original code (for Youth_original) used lowercase variables
foreach var of varlist *{
	rename `var' `=lower("`var'")'
	}
*/


save "/home/icomercial/Jorge/NH-secure/Youth_original2.dta", replace
