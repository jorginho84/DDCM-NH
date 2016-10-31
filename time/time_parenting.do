/*

This do-file analyzes the correlation between labor supply (time allocation) and parent-child relationship measures

1. correlation between UI employment and parent-child measures
2. correlation between survey hours worked and parent-child measures


*/



global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"

clear
clear matrix
clear mata
set more off
set maxvar 15000



*Youth database: parenting-time variable
use "$databases/Youth_original2.dta", clear
qui: do "$codes/data_youth.do"
keep sampleid child /*identifiers
*/ o32 o31 o32 o33 o34 o35 o36 o40 o46 o48     /* older children time variables
*/ y41 y44 y45 y47 y48 y49 y51 y52 /*young children time variables*/

replace o31=. if o31==2.19

/*
label variable o31 "O31: You have to keep quiet or leave the house when PCG is at home"
label variable o32 "O32: Your PCG tries to understand your problems and worries"
label variable o33 "O33: Your PCG spends time talking with you"
label variable o34 "O34: You are happy when you are at home"
label variable o35 "O35: You talk over important plans with your PCG"
label variable o36 "O36: Often have good times at home with your PCG"
label variable o40 "O40: You feel close to your PCG"
label variable o46 "O46: Hard to be happy when your PCG is around"
label variable o48 "O48: There is real love and affection for you at home"


label variable y41 "Y41: Your PCG spends time talking with you"
label variable y44 "Y44: Does your PCG argue or yell at you a lot?"
label variable y45 "Y45: Whe you are sad, does your PCG try to make you feel better?"
label variable y47 "Y47: Is your PCG nice to you?"
label variable y48 "Y48: Does your PCG say things about you that make you feel good?"
label variable y49 "Y49: Are you happy when you're at home?"
label variable y51 "Y51: It is easy to talk with your PCG about things?"
label variable y52 "Y52: Do you have good times at home with your PCG?"

*/


destring sampleid, replace force
sort sampleid child
tempfile data_aux
save `data_aux', replace

*Recovering employment and income variables
use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Income/data_income.dta", clear
qui: do "$codes/model/wage_process/Xs.do"
merge 1:m sampleid using `data_aux'
keep if _merge==3
drop _merge

*ACA VOY! see if I have a negative corr between time measures and employment (if not, find measures)..maybe measures of time use other than employment?
oprobit o32 employment_y0 employment_y1 employment_y2 d_HS
