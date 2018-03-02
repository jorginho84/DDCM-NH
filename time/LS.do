/*
This do-file computes the effect of New Hope on labor supply using UI administrative data

The main figure: Trends of employment probability by groups, quarters since RA, and employment status at baseline

This do-file may also compute:
-the difference in employment by quarters since RA
-difference and levels by quarters in calendar time

*/

global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"

/*
robust SE for small samples. Set to hc3 for more conservatives. 

See Angrist and Pischke for more information
"robust" SE can be misleading when the sample size is small and there is no much heteroskedasticity.
*/
local SE="hc2"

/*
set diff=1 if you want to produce a graph with the impact of New Hope (\Delta employment)
set level=1 if you want to compare the level of employment between treatment and control groups
can't run both of them
*/

local diff=1
local level=0


/*
set quarter_calendar=1 if you want to compute new hope impacts (the diff and level figures) by quarter
set quarters_ra=1 if you want to compute new hope impacts (the diff and level figures) by quarters since RA
can't run both of them
*/

local quarter_calendar=0
local quarters_ra=1


/*
controls: Don't modify this. All regressions are computed with no control variables.
*/

local controls=1


/*
Employment from CSJ: choose cjs=0 if employment do not include CSJs. 
Under this condition, the levels/quarter_RA figure changes its name
Otherwise, choose csj=1 to include CSJs in the employment definition.
WARNING: set csj=0 only qhen estimating level/quarters_ra

*/


/*
Scale of graphs
*/

local scale = 1.3

local csj=1

clear
clear matrix
clear mata
set more off
set maxvar 15000

******************************************************************************************************
******************************************************************************************************
******************************************************************************************************
/*Analysis by quarter/year*/
******************************************************************************************************
******************************************************************************************************
******************************************************************************************************


if `quarter_calendar'==1{

	use "$databases/CFS_original.dta", clear
	do "$codes/data_cfs.do"
	
	
	keep sampleid p_assign emp1q* emp2q* emp3q* emp4q* csjm94* csjm95* csjm96* csjm97*
	
	*Generate monthly employment from CSJs
	
	forvalues y=94/97{
		local mm=1
		foreach month in "01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12" {
		
		*dummy variable
		gen emp_csjm`y'`month'=1 if csjm`y'`month'>0 & csjm`y'`month'!=.
		replace emp_csjm`y'`month'=0 if csjm`y'`month'==0
		
		if `mm'<=9{
			rename emp_csjm`y'`month' emp_csjm`y'`mm' /*get rid of 0's*/
		}
		
		local mm=`mm'+1
		
		
		}
	}
	
	*Generate quarterly employment from CSJ
	forvalues y=94/97{
	
		local month=1

		forvalues q=1/4{
			local month2=`month'+1
			local month3=`month2'+1
			
			gen qemp_csjm`y'`q'=1 if emp_csjm`y'`month'==1 | emp_csjm`y'`month2'==1 | emp_csjm`y'`month3'==1
			replace qemp_csjm`y'`q'=0 if emp_csjm`y'`month'==0 & emp_csjm`y'`month2'==0 & emp_csjm`y'`month3'==0
			
			local month=`month'+3
		
		
		}
	}
	
	

	/*LEVELS BY GROUP*/
	if `level'==1{
	
	
	
	
		*Renaming employment dummies
		replace emp4q93=emp4q93/100
		rename emp4q93 emp1993q4

		local nn=1
		forvalues y=94/99{
			forvalues q=1/4{

				replace emp`q'q`y'=emp`q'q`y'/100
				rename emp`q'q`y' emp19`y'q`q'
				
			}
		}

		local yy=0
		forvalues y=2000/2003{
			forvalues q=1/4{

				replace emp`q'q0`yy'=emp`q'q0`yy'/100
				rename emp`q'q0`yy' emp200`yy'q`q' 
					
			}

		local yy=`yy'+1

		}

		*Adding employment from CSJs
	
		forvalues y=94/97{
			
			forvalues q=1/4{
			
				replace emp19`y'q`q'=1 if qemp_csjm`y'`q'==1
			
			}
		
		}

		drop qemp* emp_*/*dropping csj indicators*/
		collapse (mean) emp*, by(p_assign)

		reshape long emp, i(p_assign) j(Quarter) string
		replace emp=emp*100
		label variable Quarter "Quarter"

		gen quarter2=quarterly(Quarter, "YQ")
		format quarter2 %tq
		gen RA=(p_assign=="E")

		tsset RA quarter2, quarterly

		twoway (tsline emp if p_assign=="C", recast(connected)) (tsline emp if p_assign=="E", recast(connected)),/*
		*/scheme(s2mono) legend(order(1 "Control" 2 "Treatment")  )/*
		*/ytitle(Employment (in %)) xtitle(Quarter)/*
		*/graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))
		
		graph save "$results/Time/LS_admin_calendar_level.gph", replace
		graph export "$results/Time/LS_admin_calendar_level.pdf", as(pdf) replace

	}


	/*REGRESSIONS*/
	if `diff'==1{
	
	
		*Adding employment from CSJs
	
		forvalues y=94/97{
			
			forvalues q=1/4{
			
				replace emp`q'q`y'=100 if qemp_csjm`y'`q'==1
			
			}
		
		}

		*Regressions
		xi: reg emp4q93 i.p_assign, vce(`SE')
		mat beta=e(b)
		mat variance=e(V)
		mat betas=(beta[1,1], beta[1,1]-1.96*variance[1,1]^.5, beta[1,1]+1.96*variance[1,1]^.5)



		forvalues y=94/99{
			forvalues q=1/4{

				xi: reg emp`q'q`y' i.p_assign, vce(`SE')
				mat beta=e(b)
				mat variance=e(V)
				mat betas=betas\(beta[1,1],beta[1,1]-1.96*variance[1,1]^.5,beta[1,1]+1.96*variance[1,1]^.5)
				
				
			}
		}

		local yy=0
		forvalues y=2000/2003{
			forvalues q=1/4{

				xi: reg emp`q'q0`yy' i.p_assign, vce(`SE')
				mat beta=e(b)
				mat variance=e(V)
				mat betas=betas\(beta[1,1],_b[_Ip_assign_2] - invttail(e(df_r),0.05)*_se[_Ip_assign_2],/*
				*/ _b[_Ip_assign_2] + invttail(e(df_r),0.05)*_se[_Ip_assign_2])
				
					
			}

		local yy=`yy'+1

		}

		svmat betas
		drop if betas1==.

		gen quarter_aux="1993q3" if _n==1

		local nn=2
		forvalues y=1994/2003{
			forvalues q=1/4{
				replace quarter_aux="`y'q`q'" if _n==`nn'
				local nn=`nn'+1
			}

		}

		keep betas* quarter_aux
		gen quarter=quarterly(quarter_aux, "YQ")
		format quarter %tq

		tsset quarter, quarterly

		twoway (tsline betas1, recast(connected)) (tsline betas2, recast(line) lpattern(dash)) (tsline betas3, recast(line) lpattern(dash)),/*
		*/scheme(s2mono)/*
		*/ytitle({&Delta}employment (in %)) xtitle(Quarter) legend(off)/*
		*/graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))
		
		graph save "$results/Time/LS_admin_calendar_diff.gph", replace
		graph export "$results/Time/LS_admin_calendar_diff.pdf", as(pdf) replace
		


	}


}


*************************************************************************************
*************************************************************************************
*************************************************************************************
/*In this part I compute impacts by quarters since RA*/

*************************************************************************************
*************************************************************************************
*************************************************************************************


if `quarters_ra'==1{



	use "$databases/CFS_original.dta", clear
	do "$codes/data_cfs.do"
/*
	********************************************************************************
	*Recovering information on children
	sort sampleid
	tempfile data_cfs
	save `data_cfs', replace

	use "$databases/Youth_original2.dta", clear
	keep sampleid child zboy agechild
	destring sampleid, force replace
	reshape wide zboy agechild, i(sampleid) j(child)
	sort sampleid
	merge 1:1 sampleid using `data_cfs'

	keep if _merge==3
	drop _merge

	*Keep if at least one of the two children is a boy and young
	keep if (zboy1==1 | zboy2==1) & (agechild1<=7 | agechild2<=7)
	drop zboy* agechild*

	********************************************************************************
*/
	keep sampleid p_assign p_radatr curremp /*
	*/emp1q* emp2q* emp3q* emp4q*  /*employment variables from UI
	*/csjm94* csjm95* csjm96* csjm97* /*amount from CSJs*/

	*Generate monthly employment from CSJs
	
	forvalues y=94/97{
		local mm=1
		foreach month in "01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12" {
		
		*dummy variable
		gen emp_csjm`y'`month'=1 if csjm`y'`month'>0 & csjm`y'`month'!=.
		replace emp_csjm`y'`month'=0 if csjm`y'`month'==0
		
		if `mm'<=9{
			rename emp_csjm`y'`month' emp_csjm`y'`mm' /*get rid of 0's*/
		}
		
		local mm=`mm'+1
		
		
		}
	}
	
	*Generate quarterly employment from CSJ
	forvalues y=94/97{
	
		local month=1

		forvalues q=1/4{
			local month2=`month'+1
			local month3=`month2'+1
			
			gen qemp_csjm`y'`q'=1 if emp_csjm`y'`month'==1 | emp_csjm`y'`month2'==1 | emp_csjm`y'`month3'==1
			replace qemp_csjm`y'`q'=0 if emp_csjm`y'`month'==0 & emp_csjm`y'`month2'==0 & emp_csjm`y'`month3'==0
			
			local month=`month'+3
		
		
		}
	}
	
	
	
	*Quarter of RA
	replace p_radatr=p_radatr+19000000
	tostring p_radatr, force replace
	gen ra_quarter=qofd(date(p_radatr,"YMD"))
	format ra_quarter %tq
	tab ra_quarter

	*Generate employment in quarter number X since RA

	replace emp4q93=emp4q93/100
	rename emp4q93 emp1993q4

	local nn=1
	forvalues y=94/99{
		forvalues q=1/4{

			replace emp`q'q`y'=emp`q'q`y'/100
			rename emp`q'q`y' emp19`y'q`q'
			
		}
	}

	local yy=0
	forvalues y=2000/2003{
		forvalues q=1/4{

			replace emp`q'q0`yy'=emp`q'q0`yy'/100
			rename emp`q'q0`yy' emp200`yy'q`q' 
				
		}

	local yy=`yy'+1

	}

	*Adding employment from CSJs: CSJ==1
	
	if `csj'==1{
		forvalues y=94/97{
			
			forvalues q=1/4{
			
				replace emp19`y'q`q'=1 if qemp_csjm`y'`q'==1
			
			}
		
		
		}
	}
	
	*Reshaping to build a panel
	drop emp_* /*drop csj indicators*/
	keep emp* sampleid ra_quarter
	reshape long emp, i(sampleid) j(quarter_aux) string
	gen quarter=quarterly(quarter_aux, "YQ")
	format quarter %tq

	*Quarters since RA
	gen quarters_ra=quarter-ra_quarter
	keep quarters_ra sampleid emp
	tab quarters_ra/*this is to see how many obs*/


	*Reshape again to build the graph using collapse
	replace quarters_ra=quarters_ra+8/*trick to reshape*/
	reshape wide emp, i(sampleid) j(quarters_ra) 

	*recovering RA
	sort sampleid
	tempfile data_aux
	save `data_aux', replace
	use "$databases/CFS_original.dta", clear
	do "$codes/data_cfs.do"
	
	/*
	********************************************************************************
	*Recovering information on children
	sort sampleid
	tempfile data_cfs
	save `data_cfs', replace

	use "$databases/Youth_original2.dta", clear
	keep sampleid child zboy agechild
	destring sampleid, force replace
	reshape wide zboy agechild, i(sampleid) j(child)
	sort sampleid
	merge 1:1 sampleid using `data_cfs'

	keep if _merge==3
	drop _merge

	*Keep if at least one of the two children is a boy and young
	keep if (zboy1==1 | zboy2==1) & (agechild1<=7 | agechild2<=7)
	drop zboy* agechild*

	********************************************************************************
	*/
	
	keep sampleid p_assign curremp
	sort sampleid
	merge 1:1 sampleid using `data_aux'
	drop _merge
	
	
	********************************************************************************
	if `controls'==1{

		do "$codes/time/Xs.do"
		local control_var age_ra i.marital i.ethnic d_HS higrade i.pastern2
	
	}
	
	
	*******************************************************************************
	
	*Dropping 50 observations with no children
	do "$codes/time/drop_50.do"

	********************************************************************************
	/*
	*To compute baseline av
	
	egen baseline = rowmean(emp8-emp19)	

	sum baseline if p_assign=="C"
	sum baseline if p_assign=="C" & d_young==0
	sum baseline if p_assign=="C" & d_young==1
	
	*/
	
	*Matrix of pvalues and confidence intervals
	
	*Saving data for analysis of hours.do
	save "$results/Time/data_emp.dta", replace
	

	*Getting child age info
	tempfile data_aux
	save `data_aux', replace
	use "$databases/Youth_original2.dta", clear
	keep sampleid kid1dats
	destring sampleid, force replace
	destring kid1dats, force replace
	format kid1dats %td
	gen year_birth=yofd(kid1dats)
	drop kid1dats

	bysort sampleid: egen seq_aux=seq()
	reshape wide year_birth,i(sampleid) j(seq_aux	)
	merge 1:1 sampleid using `data_aux'
	keep if _merge==3
	drop _merge

	*child age at baseline
	gen year_ra = substr(string(p_radaym),1,2)
	destring year_ra, force replace
	replace year_ra = 1900 + year_ra

	gen agechild1_ra =  year_ra - year_birth1
	gen agechild2_ra =  year_ra - year_birth2

	*Dummy: at least 1 child less than 6 years of age by two years after baseline
	gen d_young = (agechild1_ra + 2 <=6) | (agechild2_ra + 2 <=6)
	
	stop!!

	**Overall**
	
	forvalues y=0/45{
		replace emp`y'=emp`y'*100
		qui xi: reg emp`y' i.p_assign , vce(`SE')
		if `y'==0{
			mat betasx=_b[_Ip_assign_2]
			mat betas=(_b[_Ip_assign_2],_b[_Ip_assign_2] - invttail(e(df_r),0.025)*_se[_Ip_assign_2],/*
			*/ _b[_Ip_assign_2] + invttail(e(df_r),0.025)*_se[_Ip_assign_2])
			qui: test _Ip_assign_2=0
			mat pvalues=r(p)

		}
		else{
			mat betasx=betasx\_b[_Ip_assign_2]
			mat betas=betas\(_b[_Ip_assign_2],_b[_Ip_assign_2] - invttail(e(df_r),0.025)*_se[_Ip_assign_2],/*
			*/ _b[_Ip_assign_2] + invttail(e(df_r),0.025)*_se[_Ip_assign_2])
			qui: test _Ip_assign_2=0
			mat pvalues=pvalues\r(p)
		
		}
		
	}

	**By participant with young/old children **
	
	forvalues status=0/1{/*the sample loop*/
		forvalues y=0/45{

			qui xi: reg emp`y' i.p_assign  if d_young==`status', vce(`SE')
			
			if `y'==0{
				mat betasx_`status'=_b[_Ip_assign_2]
				mat betas_`status' = (_b[_Ip_assign_2],_b[_Ip_assign_2] - invttail(e(df_r),0.025)*_se[_Ip_assign_2],/*
				*/ _b[_Ip_assign_2] + invttail(e(df_r),0.025)*_se[_Ip_assign_2])
				qui: test _Ip_assign_2=0
				mat pvalues_`status'=r(p)

			}
			else{
				mat betasx_`status'=betasx_`status'\_b[_Ip_assign_2]
				mat betas_`status' = betas_`status'\(_b[_Ip_assign_2],_b[_Ip_assign_2] - invttail(e(df_r),0.025)*_se[_Ip_assign_2],/*
				*/ _b[_Ip_assign_2] + invttail(e(df_r),0.025)*_se[_Ip_assign_2])
				qui: test _Ip_assign_2=0
				mat pvalues_`status'=pvalues_`status'\r(p)


			}

			
		}
	}
	
	
	/*LEVELS BY GROUP*/
	
	if `level'==1{
	
		***Overall*****
		preserve
		
		collapse (mean) emp*, by(p_assign)
		reshape long emp, i(p_assign) j(quarter)
		replace quarter=quarter-8 /*back to the original number*/
		
		*Re-ordering to make the p-value label on top
		gen p_assign_aux=1 if p_assign=="E"
		replace p_assign_aux=2 if p_assign=="C"
		sort p_assign_aux quarter
		drop p_assign_aux

		*Recovering p-value for labels
		svmat pvalues
		svmat betasx
		
		list quarter betasx1 
		

		*This is the pvalue label
		gen label_aux=""
		replace label_aux="*" if pvalues1<=0.1
		replace label_aux="**" if pvalues1<=0.05
		replace label_aux="***" if pvalues1<=0.01
		
		gen mean_aux1=emp if p_assign=="E" & pvalues1<=0.01
		gen mean_aux2=emp if p_assign=="E" & pvalues1<=0.05 &  pvalues1>0.01
		gen mean_aux3=emp if p_assign=="E" & pvalues1<=0.1 &  pvalues1>0.05

		*Number of obs=745 for quarter>=-3 & quarter<=32
		/*
		*Use this one if you want an * above
		twoway (connected emp quarter if p_assign=="E" & quarter>=-3 & quarter<=32, lpattern(solid) mlabel(label_aux) mcolor(black) msize(tiny) /*
		*/lwidth(thin) mlabgap(vsmall) mlabcolor(blue) mlabposition(12) mlabsize(medium))
		*/
		
		 twoway (line emp quarter if p_assign=="E" & quarter>=-3 & quarter<=32, lpattern(solid) lwidth(medthick) ) /*
		 */ (scatter mean_aux1 quarter if p_assign=="E" & quarter>=-3 & quarter<=32,  msymbol(circle) mcolor(blue) mfcolor(blue)) /*
		*/ (scatter mean_aux2 quarter if p_assign=="E" & quarter>=-3 & quarter<=32,  msymbol(circle) mcolor(blue) mfcolor(ltblue)) /*
		*/ (scatter mean_aux3 quarter if p_assign=="E" & quarter>=-3 & quarter<=32,  msymbol(circle) mcolor(blue) mfcolor(none)) /*
		*/ (line emp quarter if p_assign=="C" &  quarter>=-3 & quarter<=32, lpattern(dash) lwidth(medthick)),/*
		*/scheme(s2mono) legend(order(1 "Treatment" 5 "Control")  )/*
		*/ytitle(Employment (in %)) xtitle(Quarters since RA)/*
		*/graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white)) /*
		*/ ylabel(, nogrid) ylabel(30(10)100)  /*
		*/  xline(12, lcolor(red)) xline(0, lcolor(red)) scale(`scale')
		
		
		*How much was the increase:
		sum betasx1 if quarter<=12 & quarter>=0 & p_assign=="E"
		sum betasx1 if quarter<=3 & quarter>=0 & p_assign=="E"
		
		*list betasx1 if  quarter<=12 & quarter>=0 & p_assign=="E"
		sum emp if  quarter<=12 & quarter>=0 & p_assign=="C"
		
		
		
		if `csj'==0{
			graph save "$results/Time/LS_admin_qra_level_NoCSJ.gph", replace
			graph export "$results/Time/LS_admin_qra_level_NoCSJ.pdf", as(pdf) replace
		}
		
		else{
			graph save "$results/Time/LS_admin_qra_level.gph", replace
			graph export "$results/Time/LS_admin_qra_level.pdf", as(pdf) replace
		}
		
		
				
		
		***By employment groups***
		restore
		*There are 53 missing values
				
		
		collapse (mean) emp*, by(p_assign d_young)
		reshape long emp, i(p_assign d_young) j(quarter)
		replace quarter=quarter-8 /*back to the original number*/
		
		*Recovering old children
		gen p_assign_aux=1 if p_assign=="E"
		replace p_assign_aux=2 if p_assign=="C"
		sort p_assign_aux d_young quarter 
		svmat pvalues_0
		

		gen emp_aux=1 if d_young==1
		replace emp_aux=2 if d_young==0
		sort p_assign_aux emp_aux quarter 
		svmat pvalues_1
		
		
		
		gen label_aux=""
		replace label_aux="*" if pvalues_01<=0.1 & d_young==0
		replace label_aux="**" if pvalues_01<=0.05 & d_young==0
		replace label_aux="***" if pvalues_01<=0.01 & d_young==0

		replace label_aux="*" if pvalues_11<=0.1 & d_young==1
		replace label_aux="**" if pvalues_11<=0.05 & d_young==1
		replace label_aux="***" if pvalues_11<=0.01 & d_young==1
		
		gen mean_aux1_0=emp if p_assign=="E" & pvalues_01<=0.01 & d_young==0
		gen mean_aux2_0=emp if p_assign=="E" & pvalues_01<=0.05 &  pvalues_01>0.01 & d_young==0
		gen mean_aux3_0=emp if p_assign=="E" & pvalues_01<=0.1 &  pvalues_01>0.05 & d_young==0

		gen mean_aux1_1=emp if p_assign=="E" & pvalues_11<=0.01 & d_young==1
		gen mean_aux2_1=emp if p_assign=="E" & pvalues_11<=0.05 &  pvalues_11>0.01 & d_young==1
		gen mean_aux3_1=emp if p_assign=="E" & pvalues_11<=0.1 &  pvalues_11>0.05 & d_young==1
		
		twoway (line emp quarter if p_assign=="E" & quarter>=-3 & quarter<=32 & d_young==0, lwidth(medthick)) /*
		*/ (scatter mean_aux1_0 quarter if p_assign=="E" & quarter>=-3 & quarter<=32 & d_young==0,  msymbol(circle) mcolor(blue) mfcolor(blue)) /*
		*/ (scatter mean_aux2_0 quarter if p_assign=="E" & quarter>=-3 & quarter<=32 & d_young==0,  msymbol(circle) mcolor(blue) mfcolor(ltblue)) /*
		*/ (scatter mean_aux3_0 quarter if p_assign=="E" & quarter>=-3 & quarter<=32 & d_young==0,  msymbol(circle) mcolor(blue) mfcolor(none)) /*
		*/(line emp quarter if p_assign=="C" & quarter>=-3 & quarter<=32 & d_young==0,  lpattern(dash) lwidth(medthick)),/*
		*/scheme(s2mono) legend(order(1 "Treatment" 5 "Control")  )/*
		*/ytitle(Employment (in%)) xtitle(Quarters since RA)/*
		*/graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white)) /*
		*/ ylabel(, nogrid) ylabel(30(10)100) /*
		*/  xline(12, lcolor(red)) xline(0, lcolor(red)) scale(`scale')
		*
		
		if `csj'==0{
			graph save "$results/Time/LS_admin_qra_level_unemployed_NoCSJ.gph", replace
			graph export "$results/Time/LS_admin_qra_level_unemployed_NoCSJ.pdf", as(pdf) replace
		}
		else{
			graph export "$results/Time/LS_admin_qra_level_old.pdf", as(pdf) replace
		}
		twoway (line emp quarter if p_assign=="E" & quarter>=-3 & quarter<=32 & d_young==1, lpattern(solid) lwidth(medthick) ) /*
		*/ (scatter mean_aux1_1 quarter if p_assign=="E" & quarter>=-3 & quarter<=32 & d_young==1,  msymbol(circle) mcolor(blue) mfcolor(blue)) /*
		*/ (scatter mean_aux2_1 quarter if p_assign=="E" & quarter>=-3 & quarter<=32 & d_young==1,  msymbol(circle) mcolor(blue) mfcolor(ltblue)) /*
		*/ (scatter mean_aux3_1 quarter if p_assign=="E" & quarter>=-3 & quarter<=32 & d_young==1,  msymbol(circle) mcolor(blue) mfcolor(none)) /*
		*/(line emp quarter if p_assign=="C" & quarter>=-3 & quarter<=32 & d_young==1,  lpattern(dash) lwidth(medthick)),/*
		*/scheme(s2mono) legend(order(1 "Treatment" 5 "Control")  )/*
		*/ytitle(Employment (in%)) xtitle(Quarters since RA)/*
		*/graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white)) /*
		*/ ylabel(, nogrid) ylabel(30(10)100)  /*
		*/  xline(12, lcolor(red)) xline(0, lcolor(red)) scale(`scale')
		
		if `csj'==0{
			graph save "$results/Time/LS_admin_qra_level_employed_NoCSJ.gph", replace
			graph export "$results/Time/LS_admin_qra_level_employed_NoCSJ.pdf", as(pdf) replace
		}
		
		else{
			graph export "$results/Time/LS_admin_qra_level_young.pdf", as(pdf) replace
		}
		
	}
	
	/*REGRESSIONS*/
	if `diff'==1{
		
		



		svmat betas
		svmat betas_0
		svmat betas_1
		svmat pvalues
		svmat pvalues_0
		svmat pvalues_1
		drop if betas1==.

		*Back to quarters since RA
		egen quarter=seq()
		replace quarter=quarter-9

		*Labels for significance
		gen mean_aux=betas1 if pvalues1<=0.05
		gen mean_aux_0=betas_01 if pvalues_01<=0.05
		gen mean_aux_1=betas_11 if pvalues_11<=0.05

		/*
		To get av estimates
		sum betas1 if quarter>=0 & quarter<=11
		sum betas_01 if quarter>=0 & quarter<=11
		sum betas_11 if quarter>=0 & quarter<=11
		*/

		*The figure
		twoway (connected betas1 quarter if quarter>=-3 & quarter<=32, msymbol(circle) mlcolor(blue) mfcolor(white) ) /*
		*/ (scatter mean_aux quarter if quarter>=-3 & quarter<=32, msymbol(circle) mlcolor(blue) mfcolor(blue)) /* 
		*/(line betas2 quarter if quarter>=-3 & quarter<=32,lpattern(dash)) /*
		*/(line betas3 quarter if quarter>=-3 & quarter<=32,lpattern(dash)),/*
		*/xline(12, lcolor(red)) yline(0, lcolor(black))/*
		*/ytitle("Effect on employment (in %)") xtitle("Quarters since RA") legend(off)/*
		*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) /*
		*/plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
		*/ ylabel(-20(10)35, nogrid) scale(1.2) scheme(s2mono) 
		
		graph export "$results/Time/LS_admin_qra_diff.pdf", as(pdf) replace

		twoway (connected betas_01 quarter if quarter>=-3 & quarter<=32,mlcolor(blue) mfcolor(white) ) /*
		*/ (scatter mean_aux_0 quarter if quarter>=-3 & quarter<=32, msymbol(circle) mlcolor(blue) mfcolor(blue)) /* 
		*/(line betas_02 quarter if quarter>=-3 & quarter<=32,lpattern(dash)) /*
		*/(line betas_03 quarter if quarter>=-3 & quarter<=32,lpattern(dash)),/*
		*/xline(12, lcolor(red)) yline(0, lcolor(black))/*
		*/ytitle("Effect on employment (in %)") xtitle("Quarters since RA") legend(off)/*
		*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) /*
		*/plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
		*/ ylabel(-20(10)35, nogrid) scale(1.2) scheme(s2mono) 
		
		graph export "$results/Time/LS_admin_qra_diff_old.pdf", as(pdf) replace

		twoway (connected betas_11 quarter if quarter>=-3 & quarter<=32,mlcolor(blue) mfcolor(white) ) /*
		*/ (scatter mean_aux_1 quarter if quarter>=-3 & quarter<=32, msymbol(circle) mlcolor(blue) mfcolor(blue)) /* 
		*/(line betas_12 quarter if quarter>=-3 & quarter<=32,lpattern(dash)) /*
		*/(line betas_13 quarter if quarter>=-3 & quarter<=32,lpattern(dash)),/*
		*/xline(12, lcolor(red)) yline(0, lcolor(black))/*
		*/ytitle("Effect on employment (in %)") xtitle("Quarters since RA") legend(off)/*
		*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) /*
		*/plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
		*/ ylabel(-20(10)35, nogrid) scale(1.2) scheme(s2mono) 
		
		graph export "$results/Time/LS_admin_qra_diff_young.pdf", as(pdf) replace

	}

}
