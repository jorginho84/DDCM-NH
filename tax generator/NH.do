/*
This do-file computes earnings disposable income under the NH program
The parameters vary by number of children. They are fixed by year (1995-1997)

input: individual and family earnings. number of children. family size (married or not).

output:
-wage subsidy components database (1). These use individual earnings. independent of 2nd-earners and family composition
-child allowances databses. These use family earnings

*/

global results "C:\Users\Jorge\Dropbox\Chicago\Research\Human capital and the household\results\Taxes"
set more off
clear

set obs 40000 /*grid: until $25,000*/

*Gross earnings
egen pwages=seq() /*same grid for individual and family earnings*/


**************************************
*The wage subsidy
**************************************
preserve

gen Wsubsidy=.
replace Wsubsidy=0.25*pwages if pwages<=8500
replace Wsubsidy=3825-0.2*pwages if pwages>8500
replace Wsubsidy=0 if Wsubsidy<0 /*no taxes in NH*/

keep pwages Wsubsidy
save  "$results\wage_subsidy.dta", replace


restore


/*

******************************

The child allowance

******************************



It varies by number of children, household composition, and year

**Let \bar{E} be the level of earnings where the allowance is zero. Let x* the maximum amount of allowance.
Let E be the level of family earnings. The amount per child follows:

x* if E<=8500

alpha+beta*E if E>8500, where

beta=8500 - \bar{E}
alpha=x* - beta*8500

**Let n be the number of children. x* is determined by:

x*=1700-100n if n<=4
x*=1300 if n>4

**bar{E} follows:

\bar{E}=max{30,000, 200% poverty line},

where poverty lines:
1995: 7470(one person) +2560(additional person). 15150 (four-person family)
1996: 7740(one person) +2620(additional person). 15600 (four-person family)
1997: 7890(one person) +2720(additional person). 16050 (four-person family)

This implies that for a family of four or more (increments of 900):
1995: \bar{E}= 30,000+300
1996: \bar{E}= 30,000+1,200
1997: \bar{E}= 30,000+2,100

For a family of 3 or less, \bar{E}=30,000

**the input in this case is family earnings (not individual's)

*/

forvalues year=1995/1997 { /*year loop*/

	forvalues married=0/1 {   /*married loop*/

		forvalues nch=0/5{       /* number of children loop*/
			
			preserve
			
			*initial per-child allowance
			if `nch'<=4{
				local xstar=1700-`nch'*100
			}
			else{
				local xstar=1300
			}
			
			*parameters of per-child child allowance
			local fam_size=`married'+`nch'+1
			
			*fade-out earnings level
			if `fam_size'<4{
				local bar_E=30000
			}
			
			else{
				if `year'==1995{
					local bar_E=30000+300
				}
				if `year'==1996{
					local bar_E=30000+1200
				}
				if `year'==1997{
					local bar_E=30000+2100
				}
			}
			
			
			local Beta=`xstar'/(8500-`bar_E')
			local Alpha=`xstar'-`Beta'*8500
			
			gen childa=. /*per-child subsidy*/
			replace childa= `xstar' if pwages<=8500
			replace childa=`Alpha'+`Beta'*pwages if pwages>8500
			
			*total child allowance=per-child * number of children
			gen total_childa=childa*`nch'
			replace total_childa=0 if total_childa<0 /*no taxes*/
			keep pwages total_childa

			save  "$results\ChildAllowance_year`year'_married`married'_ch`nch'.dta", replace 
			restore
		}

	}

}


/*

use "C:\Users\Jorge\Dropbox\Chicago\Research\Human capital and the household\results\Taxes\ChildAllowance_year1997_married1_ch4.dta", clear

twoway (scatter total_childa pwages)

*/

