/*
This do-file computes the mediation table using the same sample
of the model

*/


global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Mediation"

/*
robust SE for small samples. Set to hc3 for more conservatives. 

See Angrist and Pischke for more information
"robust" SE can be misleading when the sample size is small and there is no much heteroskedasticity.
*/
local SE="hc2"


clear
clear matrix
clear mata
set maxvar 15000
set more off

use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_theta_v2.dta", clear


*Standardized measures
foreach x of numlist 2 5 8{
rename skills_t`x' skills_t`x'_aux
egen skills_t`x'=std(skills_t`x'_aux)

}

*Leisure: 148-hours
foreach x of numlist 1 4 7{
	gen l_t`x'=148-hours_t`x'
	
}

*Considering income per capita
gen incomepc_t1=(total_income_y1-cc_pay_t1*12)/(1 + nkids_year2 + married_year2)
gen incomepc_t4=(total_income_y4-cc_pay_t4*12)/(1 + nkids_year5 + married_year5)
gen incomepc_t7=(total_income_y7)/(1 + nkids_year8 + married_year8)

replace incomepc_t1=0 if incomepc_t1<0
replace incomepc_t4=0 if incomepc_t4<0
replace incomepc_t7=0 if incomepc_t7<0


*Age of child
foreach x of numlist 1 2 4 5 7 8{
	gen age_t`x'=age_t0+`x'
}

replace d_CC2_t1=0  if age_t2>6 & d_CC2_t1!=.


*******************************************************************************************************************
**********************************YEAR-2 REGRESSION****************************************************************
*******************************************************************************************************************

*ATE: sample: young old while in New Hope
qui xi: reg skills_t2 i.p_assign if age_t2<=6
local cont_total_2_obs=string(round(_b[_Ip_assign_2],0.01),"%3.2f")
qui xi: reg skills_t2 i.p_assign if age_t2>6
local cont_total_3_obs=string(round(_b[_Ip_assign_2],0.01),"%3.2f")
qui xi: reg skills_t2 i.p_assign 
local cont_total_1_obs=string(round(_b[_Ip_assign_2],0.01),"%3.2f")

forvalues x=1/3{ /*the age loop*/

	
	if `x'==1{
		qui xi: reg skills_t2 i.p_assign d_CC2_t1 incomepc_t1 l_t1 age_ra d_marital_2 d_HS2	
	}
	else if `x'==2{
		qui xi: reg skills_t2 i.p_assign d_CC2_t1 incomepc_t1 l_t1 age_ra d_marital_2 d_HS2 if age_t2<=6
	}
	else{
		qui xi: reg skills_t2 i.p_assign d_CC2_t1 incomepc_t1 l_t1 age_ra d_marital_2 d_HS2 if age_t2>6
	}

	local n_`x'=e(N)
	local b_tau_`x'=_b[_Ip_assign_2]
	local alpha_d_CC2_t1_`x'=_b[d_CC]
	local alpha_incomepc_t1_`x'=_b[incomepc_t1]
	local alpha_l_t1_`x'=_b[l_t1]


	*Contributions of measured inputs
	foreach variable of varlist d_CC2_t1 incomepc_t1 l_t1{
		if `x'==1{
			qui xi: reg `variable' i.p_assign	
		}
		else if `x'==2{
			qui xi: reg `variable' i.p_assign if age_t2<=6
		}
		else{
			qui xi: reg `variable' i.p_assign if age_t2>6
		}
		
				
		*local cont_`variable'_`x'=string(round(_b[_Ip_assign_2]*`alpha_`variable'_`x'',0.01),"%9.2f")
		local cont_`variable'_`x'=_b[_Ip_assign_2]*`alpha_`variable'_`x''
		


		
		
	}

	*Contribution of unmeasured
	*local cont_tau_`x' = string(round(`b_tau_`x'',0.01),"%9.2f")
	local cont_tau_`x' = `b_tau_`x''
	
		
}

*Making % contributions
forvalues x=1/3{
	local cont_total_`x' = 	`cont_d_CC2_t1_`x'' + `cont_incomepc_t1_`x'' + `cont_l_t1_`x'' + `cont_tau_`x''
	

	foreach variable in l_t1 incomepc_t1 d_CC2_t1 tau{
		local cont_`variable'_`x'_pc = `cont_`variable'_`x''/`cont_total_`x''
		
		*Making them strings
		local cont_`variable'_`x'_pc = string(round(`cont_`variable'_`x'_pc'*100,1),"%3.0f")
		local cont_`variable'_`x' = string(round(`cont_`variable'_`x'',0.01),"%9.2f")
	}
	local cont_total_`x' = string(round(`cont_total_`x'',0.01),"%3.2f")
	local cont_total_`x'_pc= string(100,"%3.0f")
}


*********The table**************************

file open med_table using "$results/med_table.tex", write replace
file write med_table "\begin{tabular}{llccc}"_n
file write med_table "\hline"_n
file write med_table "&& \$\sigma\$s &&  \% \bigstrut\\"_n
file write med_table "\hline"_n
local x = 1 
foreach variable in l_t1 incomepc_t1 d_CC2_t1 tau total{

	if `x'==1{
		local name "Time"
	}
	else if `x'==2{
		local name "Consumption"
	}
	else if `x'==3{
		local name "Child care"
	}
	else if `x'==4{
		local name "Unmeasured (\$\tau_t^1 - \tau_t^0\$)"
	}
	else{
		local name "Total (\$ E[A_{it}^1 - A_{it}^0] \$)"
	}
	local x = `x' + 1

	file write med_table "`name'  && `cont_`variable'_1'& & `cont_`variable'_1_pc' \bigstrut[t]\\"_n
	file write med_table "  &       & & &\\"_n
}
file write med_table " Observed  &       & `cont_total_1_obs'  & & \\"_n
file write med_table "\hline"_n
file write med_table "\end{tabular}"_n
file close med_table









