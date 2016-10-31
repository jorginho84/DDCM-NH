/*
This do-file generates 3x3 databases (years 1995-1997; children 0,1,2) containing:
-pre-tax earnings
-disposable income EITC


*/

global results "C:\Users\Jorge\Dropbox\Chicago\Research\Human capital and the household\results\Taxes"
set more off

forvalues year=1995/1997{

	forvalues children=0/2{
	
		clear
		set obs 25000 /*grid: until $25,000*/

		*Year
		gen year=`year'

		*N children (not accounting for child tax credit)
		gen depx=`children'
		
			
		*Wisconsin
		gen state=50

		*Assume everyone is single
		gen mstat=1

		*A grid of earnings
		egen pwages=seq()

		*Simulating taxes
		taxsim9,replace

		*Disposable income
		gen dincome_eitc=pwages-fiitax

		keep pwages dincome_eitc
		
		save  "$results\eitc_y`year'_ch`children'.dta", replace 
		
	}

}
