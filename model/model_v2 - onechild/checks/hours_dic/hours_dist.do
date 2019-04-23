/*
This do-file computes the distribution of hours in the sample
*/


clear
program drop _all
clear matrix
clear mata
set more off
set maxvar 15000

global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/checks"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/aux_model" /*this is where I compute aux moments*/


use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear



foreach period in 0 1 4 7{
	*kdensity hours_t`period'  if hours_t`period'>0
	*graph export "$results/hoursdensity_t`period'.pdf", as(pdf) replace

	twoway histogram hours_t`period' if hours_t`period'>0, xlabel()
	graph export "$results/hourshist_t`period'.pdf", as(pdf) replace

}


sum grossv2_y0 if grossv2_y0>0
