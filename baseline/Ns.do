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


use "$databases/CFS_original.dta", clear
qui: do "$codes/data_cfs.do"

*Eliminating 50 adults with no children
qui: do "$codes/baseline/drop_50.do"

forvalues x=-1(3)8{

	preserve

	*Restricting the sample
	
	if `x'==2{
		keep if c1!=" "
	}
	
	else if `x'==5{
		keep if piinvyy!=" "
	}
	
	else if `x'==8{
		keep if epiinvyy!=" "
	}
	
	*Treatment
	count if p_assign=="E"
	mat Ns_aux=r(N)
	
	*Control
	count if p_assign=="C"
	mat Ns_aux=Ns_aux,r(N)
	
	*Whole sample
	count
	mat Ns_aux=Ns_aux,r(N)
	
	*Saving in big matrix
	if `x'==-1{
		mat Ns=Ns_aux
	}
	
	else{
		mat Ns=Ns\Ns_aux
	}
	
	restore
}

*Saving on excel
putexcel B9=matrix(Ns) using "$results/Ns", sheet("data") modify

******************************
********CHILDREN**************
******************************
clear matrix
use "$databases/Youth_original2.dta", clear
qui: do "$codes/data_youth.do"


forvalues x=-1(3)8{

	preserve

	*Restricting the sample
	
	if `x'==2{
		keep if c1!=.
	}
	
	else if `x'==5{
		keep if piinvyy!=.
	}
	
	else if `x'==8{
		keep if epiinvyy!=.
	}
	
	*Treatment
	count if p_assign=="E"
	mat Ns_aux=r(N)
	
	*Control
	count if p_assign=="C"
	mat Ns_aux=Ns_aux,r(N)
	
	*Whole sample
	count
	mat Ns_aux=Ns_aux,r(N)
	
	*Saving in big matrix
	if `x'==-1{
		mat Ns=Ns_aux
	}
	
	else{
		mat Ns=Ns\Ns_aux
	}
	
	restore
}

*Saving on excel
putexcel B17=matrix(Ns) using "$results/Ns", sheet("data") modify


******************************************
********CHILDREN's TEACHERS**************
*****************************************

clear matrix
forvalues x=2(3)8{

	preserve

	*Restricting the sample
	
	if `x'==2{
		keep if tq1b!=.
	}
	
	else if `x'==5{
		keep if t21fl00!=.
	}
	
	else if `x'==8{
		keep if et2f03!=.
	}
	
	*Treatment
	count if p_assign=="E"
	mat Ns_aux=r(N)
	
	*Control
	count if p_assign=="C"
	mat Ns_aux=Ns_aux,r(N)
	
	*Whole sample
	count
	mat Ns_aux=Ns_aux,r(N)
	
	*Saving in big matrix
	if `x'==2{
		mat Ns=Ns_aux
	}
	
	else{
		mat Ns=Ns\Ns_aux
	}
	
	restore
}

*Saving on excel
putexcel B23=matrix(Ns) using "$results/Ns", sheet("data") modify
