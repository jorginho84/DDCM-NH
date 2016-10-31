/*

ALL ADULTS DATABASE

*/




**********************************************************************
*LABELS
label define yes_lbl 1 "Yes"



**************************************************************

************************************************************************************************************************************************
************************************************************************************************************************************************
****************************BASELINE variables************************************************************************
************************************************************************************************************************************************
************************************************************************************************************************************************
label variable p_radatr "P_RADATR: Date of RA (YYMMDD) - Raw Variable"
label variable p_assign "P_ASSIGN: Research assignment"
label variable p_radaym "P_RADAYM: YEAR,MONTH of RA (YYMM)"
label variable b_radatr "B_RADATR: BIF Random Assignment Date"


*DEMOGRAPHICS
label variable bifage "BIF age"
label variable b_bdater "B_BDATER: BIF Birthdate"
label variable p_bdatey "YEAR of Birth (YY)"
label variable p_bdatem "MONTH of Birth (MM)"
label variable p_bdated "DAY of Birth (DD)"



label variable gender "GENDER: gender"
label define gender_lbl 1 "Male" 2 "Female"
label values gender gender_lbl

label variable ethnic "ETHINC: ethnicity"
label define ethnic_lbl 1 "African-American, non-Hispanic" 2 "Hispanic" 5 "White, non-Hispanic"  3 "Asian/Pacific Islander" /*
*/4 "Native American/Alaskan Native"
label values ethnic ethnic_lbl

*HOUSEHOLD COMPOSITION
label variable marital "MARITAL: marital status"
replace marital=4 if marital==5 | marital==6
label define marital_lbl 1 "Never married" 2 "Married, living with spouse" 3 "Married, living apart" 4 "Separated, divorced, or widowed"
label values marital marital_lbl

label variable hhalone "HHALONE: Household: Live Alone"
label variable hhmother "HHMOTHER: Household: Live w/Mother"
label variable hhfather "HHFATHER: Household: Live w/Father"
label variable hhfoster "HHFOSTER: Household: Live w/Foster Parents"
label variable hhsiblin "HHSIBLIN: Household: Live w/Brother or Sister"
label variable hhspouse "HHSPOUSE: Household: Live w/Spouse"
label variable hhsigoth "HHSIGOTH: Household: Live w/Girlfriend/Boyfriend"
label variable hhownkid "HHOWNKID: Household: Live w/Own Children"
label variable hhothkid "HHOTHKID: Household: Live w/Kids of Spouse/Sig Oth"
label variable hhothrel "HHOTHREL: Household: Live w/Other Relatives"
label variable hhothers "HHOTHERS: Household: Live w/Friends/Others"

label values hhalone hhmother hhfather hhfoster  hhsiblin  hhspouse  hhsigoth  hhownkid  hhothkid  hhothrel  hhothers  yes_lbl



*WORK
label variable pastern2 "PASTERN2: Earnings Over Past 12 Months"
replace pastern2=6 if pastern2==7
label define pastern2_lbl 1 "None" 2 "$1-999" 3 "$1,000-4,999" 4 "$5,000-9,999" 5 "$10,000-14,999" 6 "$15,000 or above"
label values pastern2 pastern2_lbl


label variable currwage "CURRWAGE: current wage"
label variable everwork "EVERWORK: Ever Been Employed"
replace everwork="Yes" if everwork=="1"
replace everwork="No" if everwork=="2"

label variable work_ft "WORK_FT:Ever been employed full time (+30hrs a week)"
*label define work_lbl 1 "Yes" 2 "No"
*label values work_ft work_lbl

*does not match: some missing belong to "employed" according to report 1
label variable curremp "CURREMP: currently employed"
replace curremp="Yes" if curremp=="1"
replace curremp="No" if curremp=="2"

*does not match and don't know the categories
label variable currhrwk "CURRHRWK: Hrs per Week of Current Employmnt (Raw)"


*EDUCATION

label variable higrade "HIGRADE: Highest grade completed"
*does not match: (although close)
label variable degree "DEGREE: Highest Degree/Diploma Earned"

label variable nonecur "NONECUR: Current Enrollment: None"
label variable eslcur "ESLCUR: Current Enrollment: Eng. as 2nd Lang."
label variable abecur "ABECUR: Current Enrollment: Adult Basic Ed."
label variable gedcur "GEDCUR: Enrollment: GED Prep."
label variable voccur "VOCCUR: Current Enrollment: Voc. Ed.-Training"
label variable psecur "PSECUR: Current Enrollment: Post-Secondary Ed."
label variable jobscur "JOBSCUR: Current Enrollment: Job Search/Club"
label variable wkexcur "WKEXCUR: Current Enrollment: Work Exp. Program"
label variable hscur "HSCUR: Current Enrollment: High School"




************************************************************************************************************************************************
************************************************************************************************************************************************
****************************WORK: ADMINISTRATIVE SOURCES************************************************************************
************************************************************************************************************************************************
************************************************************************************************************************************************


*************************************************EARNINGS SUPLEMENTS FROM NEW HOPE***********************************************************
*notes: I don't knwo how "sup" variable were coded.

/*
The suplement earnings variable are the sum of the monthly variables (e.g, sup95q1=sup95m1+sup95m2+sup95m3).
These equal 0 for control individuals.

The UI data is only available on quartely basis (directly from the UI records)

Employment is defined as having at least one month of positive earnings in that quarter.

*/


rename ern1q89 ern1q98


forvalues y=94/99{
	forvalues q=1/4{

	label variable sup`y'q`q' "AMT NH EARNINGS SUPPLMT QTR `q' 19`y'"
	label variable ern`q'q`y' "UI: EARNINGS FOR Q `q' `y'"
	label variable emp`q'q`y' "UI: EMPLOYED IN Q `q' `y'"

	}
}

local yy=0

forvalues y=2000/2003{
	forvalues q=1/4{


	label variable ern`q'q0`yy' "UI: EARNINGS FOR Q `q' `y'"
	label variable emp`q'q0`yy' "UI: EMPLOYED IN Q `q' `y'"

	}

local yy=`yy'+1

}



forvalues q=1/4{
label variable sup00q`q' "SUP94Q1: AMT NH EARNINGS SUPPLMT QTR `q' 2000"

}

label variable ern4q93 "UI: EARNINGS FOR Q 4 93"
label variable emp4q93 "UI: EMPLOYED IN Q 4 93"


*Community service jobs: amount by month
*94-01 to97-12

forvalues y=94/97{
	foreach month in "01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12" {
		label variable csjm`y'`month' "CSJ amounth, `month'/`y'"
	}

}


*This has to be second-wage earner
label variable sern1q94 "Earnings Q1 94"

************************************************************************************************************************************************
************************************************************************************************************************************************
****************************THE MILWAUKEE STUDY - CORE. YEAR-2 FOLLOW UP************************************************************************
************************************************************************************************************************************************
************************************************************************************************************************************************


*********************************Job History: Section B, Employment***********************************

*According to the codebook, there are 19 spells

forvalues x=1/19{

	*This is question #20: month and year did you start this job
	label variable r`x'smof1 "R2SMOF1: job `x' start month"
	label variable r`x'syrf1 "R2SMOF1: job `x' start year"

	*This is question #21: Are you still at this job
	label variable r`x'atjf1 "R2ATJF1: still at job `x'"

	*This is question #22: month and year did you end
	label variable r`x'emof1 "R2EMOF1: job `x' end month"
	label variable r`x'eyrf1 "R2EYRF1: job `x' end month"
		

	*This is question #23: weekly hours when started
	label variable r`x'hwsf1 "R2HWSF1: weekly hours, start job `x'"

	*This is question #24: base wage when started
	label variable r`x'upsf1 "R2UPSF1: unit of pay, start job `x'"
	label variable r`x'upsf1 "R2PSTF1: pay, start job `x'"

	*This is question #25: weekly hours when finished
	label variable r`x'hwef1 "R2HWEF1: weekly hours, end job `x'"

	*This is qurstion #26: base wage when finished
	label variable r`x'upef1 "R2UPEF1: unit of pay, end job `x'"
	label variable r`x'penf1 "R2PENF1: pay, end job `x'"

	*This is question #27: receive compensation or bonuses?
	label variable r`x'obtf1 "R2OBTF1: rcvd ot/bonus/tips at job `x'"

	*This is question #28: typical week, including everything, how much paid (now/before you left)
	label variable r`x'werf1 "R2WERF1: wkly pay (inc ot/tips/bon), end job `x'"

	*This is question #29: is this job a CSJ
	label variable r`x'csjf1 "R2CSJF1: job `x' is CSJ"

}

/*
possible measures: 
-average over all hours, to have an average conditional on working. 0's on those who never worked
-construct hours worked across quarters, for each individual. 0's on those who never worked. and compare.
-average over all wages, and mutiplyit by hours. (potentially important when constructing income measures)

*/



***************************Income sources: Section C************************************************
/*

inmediate family: "people in the HH that you help to support or who help support you"
complex: HH in which there are people classified not as an inmediate family.
The questionnaire includes only individuals from the inmediate family

For i \in { respondent, spouse, partner, mother, father, foster parent (1 case), 
respondent's child (1-8), spouse's child (1-4), sibling (1-5), other relative (1-8),
non-relative (1-6) }, where i is a member of the HH (or inmediate family):

-If that member of the HH is an inmediate family member
-paid work (question 62)
-NH wage supplement (question 63a)
-Unemployment insurance (question 63b)
-Worker's compensation (question 63c)
-Child support (question 63d)
-Alimony (question 63e)
-Rent from a tenant or boarder (question 63f)
-Money from other family other than rent (question 63g)
-Food stamps (question 64h)
-AFDC cash, not counting child support or CC payments (question 64i)
-General assistance (question 64j)
-Woman, Infants, and Children Nutrition Program (WIC) (question 64k)
-Foster child payments (question 64l)
-Supplemental Security Income (SSI) for the disabled (question 64m)
-Social security (SSA) (question 64n)
-Private or government pension (question 64o)
-Refugee assistance (question 64p)
-Money from friends and family outside the HH (question 64q)
-Other source of income (question 64r)

-For children, the age is recorded

*/


*Members list
local name_list "respondant spouse partner mother father foster_parent1 respondent_child_1 respondent_child_2 respondent_child_3 respondent_child_4 respondent_child_5   respondent_child_6 respondent_child_7 respondent_child_8 spouse_child_1 spouse_child_2  spouse_child_3 spouse_child_4 sibling_1 sibling_2 sibling_3 sibling_4 sibling_5 relative_1 relative_2 relative_3 relative_4 relative_5 relative_6 relative_7 relative_8  nonrelative_1 nonrelative_2 nonrelative_3 nonrelative_4 nonrelative_5 nonrelative_6 nonrelative_7 nonrelative_8"

local i=1
foreach member in rp sp pt mo fa f1 /*
 */c1 c2 c3 c4 c5 c6 c7 c8 /*
*/o1 o2 o3 o4 s1 s2 s3 s4 s5 r1 r2 r3 r4 r5 r6 r7 r8 /*
 */n1 n2 n3 n4 n5 n6{
	
	*Assigning members to variables
	local j=1
	foreach name_aux of local name_list{
		if `j'==`i' {
			local name="`name_aux'" 
		}
		local j=`j'+1
	}
	
	*Variables
	label variable `member'apwlf1 "`name': amount paid work (question 62)"
	label variable `member'awslf1 "`name': amount NH wage supplement (question 62a)"
	label variable `member'auilf1 "`name': amount UI (question 62b)"
	label variable `member'awclf1 "`name': amount worker's compensation (question 62c)"
	label variable `member'acslf1 "`name': amount child support (question 62d)"
	label variable `member'aallf1 "`name': amount alimony (question 62e)"
	label variable `member'arelf1 "`name': amount rent from tenant (question 62f)"
	label variable `member'ahhlf1 "`name': amount from another hh member (question 62g)"
	label variable `member'afslf1 "`name': amount food stamps (question 62h)"
	label variable `member'aaflf1 "`name': amount AFDC (question 62i)"
	label variable `member'agalf1 "`name': amount general assistance (question 62j)"
	label variable `member'awilf1 "`name': amount WIC (question 62k)"
	label variable `member'afclf1 "`name': amount foster child payments (question 62l)"
	label variable `member'asilf1 "`name': amount SSI (question 62m)"
	label variable `member'asslf1 "`name': amount Social Security (question 62n)"
	label variable `member'apelf1 "`name': amount pension (question 62o)"
	label variable `member'aralf1 "`name': amount refugee assistance (question 62p)"
	label variable `member'afflf1 "`name': amount family/friends outside HH (question 62q)"
	label variable `member'aoslf1 "`name': amount other sources (question 62r)"
		
	
	
	
	
		
	local i=`i'+1

}




*****************************************************************************************************


*SECTION A: TRAINING ACTIVITIES  AND EMPLOYMENT PROGRAMS
label variable c1 "C1: Since RA, attended classes on preparing resumes and job apps"
label variable c2 "C2: If yes, how many hours per week"
label variable c2_dk "C2: If yes, how many hours per week (categories)"
label variable c3 "C3: If yes, how many weeks"
label variable c3_dk "C2: If yes, how many weeks (categories)"
label variable c4 "C4: Since RA, received training certificate, license, diploma or degree"
label variable c5_1 "C5: If yes, HS diploma?"
label variable c5_2 "C5: If yes, GED?"
label variable c5_3 "C5: If yes, trade license/certificate?"
label variable c5_4 "C5: If yes, associate's degree?"
label variable c5_5 "C5: If yes, college degree?"
*questions 7-9: all classes taken (details: types and hours)
label variable c13 "C13: If part of JOBS program"
label variable c14 "C14: unpaid job as a requirement for  AFDC?"

*SECTION B: EMPLOYMENT
label variable c17 "C17: since RA, worked at all?"
label variable c18 "C18: Work on and off, odd jobs, paid work in their own homes. anything like that?"
*Note:I don't have c19-30: details of every job since RA (hours worked, wages, etc)

*Box number 5: current/most recent (worked more hours)
label variable cboxb5 "IS SELECTED JOB/ACTIVITY SELF-EMPLOY"

*Number of spells: significant
label variable c_1count "C_1COUNT: # OF PERIODS OF EMPLOYMENT"

*Currently working: significant.  
label variable cboxb6 ": CBOXB6 IS R CURRENTLY WRKING"



label variable c43 "C43: If not working (c18), have you been doing anything to find work during the last four weeks?"

label variable c44a "C44: things you have done to find a job: Interview w/Employer"
label variable c44b "C44: things you have done to find a job: Public employment agency"
label variable c44c "C44: things you have done to find a job: Private employment agency"
label variable c44d "C44: things you have done to find a job: Friends or relatives"
label variable c44e "C44: things you have done to find a job: School/university employment center"
label variable c44f "C44: things you have done to find a job: New Hope Staff"
label variable c44g "C44: things you have done to find a job: JOBS staff"
label variable c44h "C44: things you have done to find a job: Sent out resumes/filled out applications"
label variable c44i "C44: things you have done to find a job: Cheked unions/professional registers"
label variable c44j "C44: things you have done to find a job: Placed or andwered ads"
label variable c44k "C44: things you have done to find a job: Looked at ads"
label variable c44l "C44: things you have done to find a job: Attended jobs programs/course"
label variable c44m "C44: things you have done to find a job: Other"
label variable c44n "C44: things you have done to find a job: Nothing"

label variable c45 "C45: How many employers have you contacted"
label variable c46 "C46: Hours spent looking for work"
label variable c50 "C50: Have you looked for job at any time since RA"
*C52: lowest hourly wage you would accept working at a new full-time job

*SECTION C: HOUSEHOLD COMPOSITION AND INCOME
label variable c53a_1 "C53a: You got married?: yes/no"
label variable c53a_2 "C53a: You got married?: Yes-month"
label variable c53a_3 "C53a: You got married?: Yes-year"
label variable c53a_4 "C53a: You got married?: Yes-month"
label variable c53a_5 "C53a: You got married?: Yes-year"

label variable c53b_1 "C53b: You got divorce/separated?: yes/no"
label variable c53b_2 "C53b: You got divorce/separated?: Yes-month"
label variable c53b_3 "C53b: You got divorce/separated?: Yes-year"
label variable c53b_4 "C53b: You got divorce/separated?: Yes-month"
label variable c53b_5 "C53b: You got divorce/separated?: Yes-year"

label variable c53c_1 "C53c: You started living with partner?: yes/no"
label variable c53c_2 "C53c: You started living with partner?: Yes-month"
label variable c53c_3 "C53c: You started living with partner?: Yes-year"
label variable c53c_4 "C53c: You started living with partner?: Yes-month"
label variable c53c_5 "C53c: You started living with partner?: Yes-year"

label variable c53d_1 "C53c: You stopped living with partner?: yes/no"
label variable c53d_2 "C53c: You stopped living with partner?: Yes-month"
label variable c53d_3 "C53c: You stopped living with partner?: Yes-year"
label variable c53d_4 "C53c: You stopped living with partner?: Yes-month"
label variable c53d_5 "C53c: You stopped living with partner?: Yes-year"

label variable c53d_1 "C53c: You had a child?: yes/no"
label variable c53d_2 "C53c: You had a child?: Yes-month"
label variable c53d_3 "C53c: You had a child?: Yes-year"
label variable c53d_4 "C53c: You had a child?: Yes-month"
label variable c53d_5 "C53c: You had a child?: Yes-year"


label variable c54 "C54: current marital status"
label variable c55 "C55: Are you currently living with a (girlfriend/boyfriend) or partner"
*note: the variable on family income are not well coded

label variable c57b "C57b: Last month, did you have any children of your own in the HH"
label variable c57d "C57d: Last month, did your spouse have any children (other than previously listed) in the HH"
label variable c59 "C59: Last month, did you or anyone in your inmediate family receive any pay from a job (including CSJ)?"


*c62: How much did you (and the other family members) earn last month? Can't find it

*SECTION D: CHILD AND DEPENDENT CARE DURING JOB-RELATED ACTIVITIES
*Note: these variables do not change across siblings.

/*CC use*/
label variable c68a "In a Head Start Program"
label variable c69a_1 "In a Head Start Program: 1ST NAME 1ST CHILD"
label variable c69a_2 "In a Head Start Program: 1ST CHILD A OR B"
label variable c69a_3 "In a Head Start Program: 1ST NAME 2ND CHILD"
label variable c69a_4 "In a Head Start Program: 2ND CHILD A OR B"
label variable c70a_1 "In a Head Start Program: # MO.S 1ST CHILD"
label variable c70a_2 "In a Head Start Program: # MO.S 2ND CHILD"


label variable c68b "Preschool, nursey, or CC other than Head Start"
label variable c69b_1 "Preschool, nursey, or CC other than Head Start: 1ST NAME 1ST CHILD"
label variable c69b_2 "Preschool, nursey, or CC other than Head Start: 1ST CHILD A OR B"
label variable c69b_3 "Preschool, nursey, or CC other than Head Start: 1ST NAME 2ND CHILD"
label variable c69b_4 "Preschool, nursey, or CC other than Head Start: 2ND CHILD A OR B"
label variable c70b_1 "Preschool, nursey, or CC other than Head Start: # MO.S 1ST CHILD"
label variable c70b_2 "Preschool, nursey, or CC other than Head Start: # MO.S 2ND CHILD"


label variable c68c "Extended day program"
label variable c69c_1 "Extended day program: 1ST NAME 1ST CHILD"
label variable c69c_2 "Extended day program: 1ST CHILD A OR B"
label variable c69c_3 "Extended day program: 1ST NAME 2ND CHILD"
label variable c69c_4 "Extended day program: 2ND CHILD A OR B"
label variable c69_5 "Extended day program: 1ST NAME 3RD CHILD"
label variable c69c_6 "Extended day program: 3RD CHILD A OR B"
label variable c69c_7 "Extended day program: 1ST NAME 4TH CHILD"
label variable c69c_8 "Extended day program: 4TH CHILD A OR B"
label variable c70c_1 "Extended day program: # MO.1STCHILD"
label variable c70c_2 "Extended day program: # MO.S 2ND CHILD"
label variable c70c_3 "Extended day program: # MO.S 3RD CHILD"
label variable c70c_4 "Extended day program: # MO.S 4TH CHILD"


label variable c68d "Another CC other than someone's home"
label variable c69d_1 "Another CC other than someone's home: 1ST CHILD NAME"
label variable c69d_2 "Another CC other than someone's home: 1ST CHILD A OR B"
label variable c69d_3 "Another CC other than someone's home: 1ST NAME 2ND CHILD"
label variable c69d_4 "Another CC other than someone's home: 2ND CHILD A OR B"
label variable c69d_5 "Another CC other than someone's home: 1ST NAME 3RD CHILD"
label variable c69d_6 "Another CC other than someone's home: 3RD CHILD A OR B"
label variable c70d_1 "Another CC other than someone's home: # MO.S 1ST CHILD"
label variable c70d_2 "Another CC other than someone's home: # MO.S 2ND CHILD"
label variable c70d_3 "Another CC other than someone's home: # MO.S 3RD CHILD"


label variable c68e "Any person other than household member"
label variable c68e_2 "Any person other than household member: YOUR RELATIONSHIP TO PERSON"
label variable c69e_1 "Any person other than household member: 1ST NAME 1ST CHLD"
label variable c69e_2 "Any person other than household member: 1ST CHILD A OR B"
label variable c69e_3 "Any person other than household member: 1ST NAME 2ND CHLD"
label variable c69e_4 "Any person other than household member: 2ND CHILD A OR B"
label variable c69e_5 "Any person other than household member: 1ST NAME 3RD CHLD"
label variable c69e_6 "Any person other than household member: 3RD CHILD A OR B"
label variable c69e_7 "Any person other than household member: 1ST NAME 4TH CHLD"
label variable c69e_8 "Any person other than household member: 4TH CHILD A OR B"
label variable c69e_9 "Any person other than household member: 1ST NAME 5TH CHLD"
label variable c69e_10 "Any person other than household member: 5TH CHILD A OR B"
label variable c70e_1 "Any person other than household member: # MO.S 1ST CHILD"
label variable c70e_2 "Any person other than household member: # MO.S 2ND CHILD"
label variable c70e_3 "Any person other than household member: # MO.S 3RD CHLD"
label variable c70e_4 "Any person other than household member: # MO.S 4TH CHILD"
label variable c70e_5 "Any person other than household member: # MO.S 5TH CHLD"

label variable c68f "Another household member"
label variable c68f_2 "Another household member: YOUR RELATIONSHIP TO"
label variable c69f_1 "Another household member: 1ST NAME 1ST CHILD"
label variable c69f_2 "Another household member: 1ST CHILD A OR B"
label variable c69f_3 "Another household member: 1ST NAME 2ND CHILD"
label variable c69f_4 "Another household member: 2ND CHILD A OR B"
label variable c69f_5 "Another household member: 1ST NAME 3RD CHILD"
label variable c69f_6 "Another household member: 3RD CHILD A OR B"
label variable c69f_7 "Another household member: 1STNAME 4TH CHILD"
label variable c69f_8 "Another household member: 4TH CHILD A OR B"
label variable c69f_9 "Another household member: 1ST NAME 5TH CHILD"
label variable c69f_10 "Another household member: 5TH CHILD A OR B"
label variable c70f_1 "Another household member: # MO.S 1 STH CHILD"
label variable c70f_2 "Another household member: # MO.S 2ND CHILD"
label variable c70f_3 "Another household member: # MO.S 3RD CHILD"
label variable c70f_4 "Another household member: # MO.S 4TH CHILD"
label variable c70f_5 "Another household member: # MO.S 5TH CHILD"

label variable c68g "NO ARRANGEMENTS"

/*CC payments: who?*/
label variable c71a "HEAD START:PAID"
label variable c72a_1 "HEAD START: RESPONDENT PAID"
label variable c72a_2 "HEAD START:SPOUSE/PARTNER PAID"
label variable c72a_3 "HEAD START:OTHR FMLY MEMBER PAID"
label variable c72a_4 "HEAD START:WLFR DEPART/JOBS PAID"
label variable c72a_5 "HEAD START:NEW HOPE PAID"
label variable c72aoth "HEAD START:OTHER PAID"
label variable c72aspfy "OTHR (SPCFY) PAID"


label variable c71b "PRE/NURSERY: PAID"
label variable c72b_1 "PRE/NURSERY: RESPONDENT PAID"
label variable c72b_2 "PRE/NURSRY: SPOUSE/PARTNER PAID"
label variable c72b_3 "PRE/NURSRY: OTHR FMLY MMBR PAID"
label variable c72b_4 "PRE/NRSRY: WLFR DPRT/JOBS PAID"
label variable c72b_5 "PRE/NRSRY: NEW HOPE PAID"
label variable c72both "PRE/NURSERY: OTHER PAID"
label variable c72bspfy "PRE/NURSERY: OTHER (SPCFY) PAID"

label variable c71c "EXTEND-DAY:PAID"
label variable c72c_1 "EXTEND-DAY: RESPONDENT PAID"
label variable c72c_2 "EXTEND-DAY: SPOUSE/PRTNR PAID"
label variable c72c_3 "EXTEND-DAY: OTHER FMLY MMBR PD"
label variable c72c_4 "EXTEND-DAY: WLFR DPRT/JOBS PD"
label variable c72c_5 "EXTEND-DAY: NEW HOPE PAID"
label variable c72coth "EXTEND-DAY: OTHER PAID"
label variable c72cspfy "EXTEND-DAY: OTHER (SPCFY) PD"

label variable c71d "ANTHR PRGRM: PAID"
label variable c72d_1 "ANTHR PRGRM: RESPONDENT PD"
label variable c72d_2 "ANTHR PRGRM: SPOUSE/PRTNR PD"
label variable c72d_3 "ANTHR PRGRM: OTHR FMLY MMBR PD"
label variable c72d_4 "ANTHR PRGRM: WLFR DPRT/JOBS PD"
label variable c72d_5 "ANTHR PRGRM: NEW HOPE PD"
label variable c72doth "ANTHR PRGRM: OTHER PAID"
label variable c72dspfy "ANTHR PRGRM: OTHR (SPCFY) PD"

label variable c71e "NON/FAM PRSN: PAID"
label variable c72e_1 "NON/FAM PRSN: RESPONDENT PAID"
label variable c72e_2 "NON/FAM PRSN: SPOUSE/PRTNR PD"
label variable c72e_3 "NON/FAM PRSN: OTHR FMLY MMBR PD"
label variable c72e_4 "NON/FAM PRSN: WLFR DPRT/JOBS PD"
label variable c72e_5 "NON/FAM PRSN: NEW HOPE PAID"
label variable c72eoth "NON/FAM PRSN: OTHER PAID"
label variable c72espfy "NON/FAM PRSN: OTHER (SPCFY) PD"

label variable c71f "FAM MEMBER: PAID"
label variable c72f_1 "FAM MEMBER: RESPONDENT PAID"
label variable c72f_2 "FAM MEMBER: SPOUSE/PARTNER PAID"
label variable c72f_3 "FAM MEMBER: OTHER FAM MMBR PAID"
label variable c72f_4 "FAM MEMBER: WLFR DPRT/JOBS PAID"
label variable c72f_5 "FAM MEMBER: NEW HOPE PAID?"
label variable c72foth "FAM MEMBER: OTHER PAID"
label variable c72fspfy "FAM MEMBER: OTHER (SPECIFY) PAID"


/*If some CC was paid*/
label variable c73 "C73: How much did you pay (own pocket) last month?"
label variable c73dk "C73: How much did you pay (own pocket): categories if don't know"

/*About the program that the child has spent most time in, if yes in CC use (c68a-d)*/
label variable c75a "CHILD A: # CHILDREN IN PROGRAM"
label variable c76a "CHILD A: # CARED FOR CHILDREN"
label variable c77a "CHILD A: HOW LIKE TO CHANGE PROGRAM"
label variable c75b "CHILD B: # CHILDREN IN PROGRAM"
label variable c76b "CHILD B: # CARED FOR CHILDREN"
label variable c77b "CHILD B: HOW LIKE TO CHANGE PROGRAM"


/*If yes in family/non-family member (c68e-f)*/
label variable c81a "CHILDA: PERSON LICENSED"
label variable c82a "CHILDA: HOW CHANGE PERSON'S CARE"
label variable c81b "CHILDB: PERSON LICENSED"
label variable c82b "CHILDB: HOW CHANGE PERSON'S CARE"


*SECTION E: ECONOMIC WELL-BEING AND CONCERNS
label variable c91 "C91: How much of the time during the past month have you felt stressed?"


*SECTION F: HEALTH AND EDUCATION
*note:variable 136-147 (education-related) are not in the database

*SECTION G: THE NEW HOPE PROJECT (Ps only)
label variable c148a "C148: Through the New Hope Project, did you get: A community service job"
label variable c148b "C148: Through the New Hope Project, did you get: A wage subsidy while working full time"
label variable c148c "C148: Through the New Hope Project, did you get: Help with child or dependent care"
label variable c148d "C148: Through the New Hope Project, did you get: Help with insurance coverage"
label variable c148e "C148: Through the New Hope Project, did you get: Help finding a full-time job"
label variable c148f "C148: Through the New Hope Project, did you get: Advice and support"
label variable c148g "C148: Through the New Hope Project, did you get: Meetings and get-togethers?"

label variable c152 "C152: lose the wage subsidy b/c you worked less than 30 hours?"
label variable c154 "C154: why didn't you receive help from NH wuith child or dependent care?"

*********************************************************************************************************************************************
*********************************************************************************************************************************************
*******************************************TWO-YEAR FOLLOW-UP (F1)***************************************************************************
*********************************************************************************************************************************************





***********************************CFS PARENTS**********************************************************************************************

*SECTION A: PARENTS TIME USE
label variable pthwjbf1 "pthwjbf1: what times did you work at a job away from home? hours worked at job past week"
label variable pthwhmf1 "PTHWHMF1: what times did you work at a job at home? hours worked at home past week"
*note: I don't know how these variable were coded
label variable pthrslf1 "PTHRSLF1: hours sleeping"
label variable pthrshf1 "PTHRSHF1 hours doing shopping or errands"
label variable p6 "P6: DO you usually get up the same time of weekdays"
label variable p7 "P7: What time you eat dinner on weekdays"
label variable p8 "P8: Do you gnerally work the same hours every workday"
label variable p14a "P14A: Does this job provide you with: Sick days with full day"
label variable p14b "P14B: Does this job provide you with: Paid vacations"
label variable p14c "P14C: Does this job provide you with: Employer-sponsored health plan"
label variable p14d "P14D: Does this job provide you with: Pension plan"
label variable p15f1 "P15: In general, how do yo feel about your time"
*note: variable p15 corresponds to the same question, but coded backwards!!!
label variable p16f1 "P15: Have time in your hands that you don't know what to do with?"
*note: variable p16 corresponds to the same question, but coded backwards!!!
label variable p19 "P19: Have a dictionary at home"

*SECTION B: CHILD CARE: SAME AS SECTION D: CHILD AND DEPENDENT CARE DURING JOB-RELATED ACTIVITIES
*notes: too many missing values.

*SECTION C: CHILDREN'S HEALTH CARE
label variable p32 "P32: Is there a particular place that Child A/B go for medical care?"
label variable p33 "P33 It is the same for child A and B?"
label variable p41_a "P41A: How long since Child A saw a health professional"
label variable p42_a "P42A: How long since Child A saw a dentist"
label variable p43_a "P43A: How would you describe child A inmunization status"
label variable p41_b "P41B: How long since Child B saw a health professional"
label variable p42_b "P42B: How long since Child B saw a dentist"
label variable p43_b "P43B: How would you describe child B inmunization status"


*SECTION D: YOU AND YOUR CHILD (CHILDA A)
label variable p44 "P44: How often do you praise your child"
label variable p45 "P45: How often do you and your child play with each other (for five minutes or more)"
label variable p46 "P45: How often do you do something special for him/her"
label variable p47 "P47: How often does your child gets away w/ womthing that should have resulted in punishment"
label variable p48 "P48: How often you get angry with him when punish"
label variable p49 "P49: How often do you feel you are having problems managing him/her in general"
label variable p50 "P50: How often when you punish him, does he ignore the punishment"
label variable p51 "P51: How often do ypu punish him/her repeatdly for the same thing"
label variable p52 "P52: My child seems to be much harder to care for than most"
label variable p53 "P53: There are some things my child does that really bother me a lot"
label variable p54 "P54: Sometimes I lose patience with him/her questions and I just don't listen"
*note: check point: the answers in p54 coincide with the CFS database.
label variable p55 "P55: I often feel angry with my child"
label variable p56 "P56: How much trouble has your child been to raise"
*items 57-61 are omitted due to copyright protection
label variable p64 "P64: How far would you like to see CHILD A go in school"
label variable p65 "P65: How far do you think will actually CHILD A go in school"
label variable p67a "P67a: Weekday, hours of TV: Before 8am"
label variable p67b "P67b: Weekday, hours of TV: Between 8am and 3pm"
label variable p67c "P67c: Weekday, hours of TV: Between 3pm and dinner"
label variable p67d "P67d: Weekday, hours of TV: After dinner time"
label variable p70 "70: Typical week, how often does you child makes the bed and put toys and things away"

*notes: items 72-106 are omitted due to copyright
*notes: items 107-111 are omitted due to copyright

*SECTION F (I ASUME THAT IS 6-12 YEARS OLD, LIKE SECTION G FROM CHILD B)
*note: p112 has to be answered by a child 6-12 years og age. p64 by younger child?). 
label variable p112 "P112: How far would you like to see CHILD A go in school"
label variable p113 "P113: How far do you think will actually CHILD A go in school"
label variable p115b "How often do you know: who is she/he with when he/she is away from home"
label variable p115c "How often do you know: where is she/he with when he/she is away from home"
label variable p117a "P117a: Weekday, hours of TV: Before 8am"
label variable p117b "P117b: Weekday, hours of TV: Between 8am and 3pm"
label variable p117c "P117c: Weekday, hours of TV: Between 3pm and dinner"
label variable p117d "P117d: Weekday, hours of TV: After dinner time"
label variable p119a "How often does you child makes the bed and put toys and things away"


*SECTION G: PARENT QUESTIONS ABOUT SELF
label variable p159 "P159: could not shake the blues"
label variable p160 "P160: just as good as other people"
label variable p162 "P162: felt depressed"
label variable p165 "P162: my life had been a failure"
label variable p168 "P168: I was happy"
label variable p170 "P170: I felt lonely"

label variable p207_1 "P207: do you hold: regular High school diploma"
label variable p207_2 "P207: do you hold: GED certificate"
label variable p207_2 "P207: do you hold: trade license or certificate"
label variable p207_2 "P207: do you hold: associate's degree"
label variable p207_2 "P207: do you hold: four-year college"
label variable p208 "P208: highest grade or year completed"
label variable p209 "P209: ethnic group"


*SECTION H: YOU AND YOUR CHILD (CHILD B)
label variable p217 "P217 How often do you praise your child"
label variable p218 "P218: How often do you and your child play with each other (for five minutes or more)"
label variable p219 "P219: How often do you do something special for him/her"
label variable p220 "P220: How often does your child gets away w/ womthing that should have resulted in punishment"
label variable p221 "P221: How often you get angry with him when punish"
label variable p222 "P222: How often do you feel you are having problems managing him/her in general"
label variable p223 "P223: How often when you punish him, does he ignore the punishment"
label variable p224 "P224: How often do ypu punish him/her repeatdly for the same thing"
label variable p225 "P225: My child seems to be much harder to care for than most"
label variable p226 "P226: There are some things my child does that really bother me a lot"
label variable p229 "P229: How much trouble has your child been to raise"
label variable p237 "P237: How far would you like to see CHILD B go in school"
label variable p238 "P238: How far do you think will actually CHILD B go in school"
label variable p240a "P240a: Weekday, hours of TV: Before 8am"
label variable p240b "P240b: Weekday, hours of TV: Between 8am and 3pm"
label variable p240c "P240c: Weekday, hours of TV: Between 3pm and dinner"
label variable p240d "P240d: Weekday, hours of TV: After dinner time"
label variable p248 "P248: About how many books CHILD B have"

*SECTION J: ABOUT CHILD B (6-12 YEARS OLD)
*note: this variable appears twice, but has less missing values
label variable p250 "How far would you like to see CHILD B go in school"
label variable p251 "P251: How far do you think will actually CHILD A go in school"
label variable p253b "How often do you know: who is she/he with when he/she is away from home"
label variable p253c "How often do you know: where is she/he with when he/she is away from home"
label variable p255a "P253a: Weekday, hours of TV: Before 8am"
label variable p255b "P253b: Weekday, hours of TV: Between 8am and 3pm"
label variable p255c "P253c: Weekday, hours of TV: Between 3pm and dinner"
label variable p255d "P253d: Weekday, hours of TV: After dinner time"
label variable p257a "How often does you child makes the bed and put toys and things away"


*OTHERS
*HMCGAYF1: HOME COGNITIVE STIM SCORE (3-5). hmcgayf1
*ERN3Q97: UI: EARNINGS FOR Q 3 97 ern3q97
*FEITC94: FEDERAL EITC 1994 - NEW ESTIMATE.
*NEICQ18: NEW EST AMT OF EITC RECEIVED IN QUARTER 18

*Parents' Psycological well-being
label variable ppearlf1 "PPEARLF1: pcg MASTERY pearlin scale"
label variable phopef1 "PHOPEF1: pcg State Hope scale"
label variable pestemf1 "PESTEMF1: Self-steem Score"
label variable pcesdf1 "PCESDF1: pcg measure of depression cesd ()"

*********************************************************************************************************************************************
*********************************************************************************************************************************************
****************************FIVE-YEAR FOLLOW-UP**********************************************************************************************
*********************************************************************************************************************************************
*********************************************************************************************************************************************




******************************Parents' interview (year-5 follow up)*************************************************************************


*SECTION A: LIVING ENVIRONMENT
label variable piq1wk "PIQ1 weeks: For how long altogether have you lived in this neighborhood"
label variable piq1mth "PIQ1 months: For how long altogether have you lived in this neighborhood"
label variable piq1yr "PIQ1 year: For how long altogether have you lived in this neighborhood"
label variable piq2 "PIQ2: As a place to live and raise children, would you say your neighborhood is (5 is excellent)"
label variable piq8 "PIQ8: Are you living in the same house or apartment as you were three years ago"
label variable piq9 "PIQ9: How many times altogether have you moved in the last three years, including your most recent move?"
label variable piq10 "PIQ10: In what month and year did your most recent move occur?"
label variable piq14 "PIQ14: How many rooms in the house"
label variable piq15 "PIQ15: family owns house? see alternatives in questionnaire"
label variable piq16 "PIQ16: How much rent"
label variable piq20 "PIQ16: Mortgage?"
label variable piq21 "PIQ21: Mortgage payment"


*SECTION B: PARENTAL AND CHILD HEALTH
label variable piq26 "PIQ21: Relative to other people your age, would you rate your overall health at the present time as . . .(5=excelent)"
label variable piq29 "PIQ29: Do you have any kind of health condition that makes it hard for you to do paid work or limits the work you can generally count on being able to do?"
label variable piq31a "PIQ31: Child has health problems requiring frequent trips to the doctor"
label variable piq31b "PIQ31: Child has behavior that is hard to control"
label variable piq31c "PIQ31: Child has any other health problem"
label variable piq32a1 "PIQ32: Child has health problems requiring frequent trips to the doctor. Child 1"
label variable piq32a2 "PIQ32: Child has health problems requiring frequent trips to the doctor. Child 2"
label variable piq32a3 "PIQ32: Child has health problems requiring frequent trips to the doctor. Child 3"
label variable piq32b1 "PIQ32: Child has behavior that is hard to control. Child 1"
label variable piq32b2 "PIQ32: Child has behavior that is hard to control. Child 2"
label variable piq32b3 "PIQ32: Child has behavior that is hard to control. Child 3"
label variable piq32c1 "PIQ32: Child has any other health problem. Child 1"
label variable piq32c2 "PIQ32: Child has any other health problem. Child 2"
label variable piq32c3 "PIQ32: Child has any other health problem. Child 3"
*NOTE:some questions related to child's health problems are not in the database

*SECTION C: EMPLOYMENT
label variable piq49 "PIQ49: Are you currently working for pay for an employer at a full-time job (>30 hours)"
label variable piq50 "PIQ50: And how about in the last 12 months?"
label variable piq51 "PIQ51: Are you currently (also) working for pay for an employer at one or more part-time jobs (<30 hours)"
label variable piq54 "PIQ54: If no in Q51, And how about in the last 12 months?"
label variable piq52 "PIQ52: How many part-time jobs do you have"
label variable piq55 "PIQ55: Doing anything to earn money"
label variable piq56 "PIQ55: How about the last 12 months?"
label variable piq62b "PIQ62b: At any time during the last year, did you receive: A raise in pay?"
label variable piq66 "PIQ66: Hours per week at this job"

label variable piq67u "PIQ67: How much are(were) you paid for this job: Types"
replace piq67u="Hour" if piq67u=="1"
replace piq67u="Week" if piq67u=="2"
replace piq67u="Month" if piq67u=="3"
replace piq67u="Year" if piq67u=="4"

label variable piq67am "PIQ67: How much are(were) you paid for this job"

label variable piq73 "PIQ73: When the job or work weve been discussing ended (see categories in questionnaire)"
label variable piq75 "PIQ75: Have you been doing anything to find work during the last four weeks?"
label variable piq76 "PIQ76: Have you interviewed with any employers or temporary agencies within the last four weeks?"

*SECTION D: HOUSEHOLD COMPOSITION AND INCOME
label variable piq93a "PIQ93: Since 3 yrs ago: got married"
label variable piq93b "PIQ93: Since 3 yrs ago: got divorced or separated"
label variable piq93c "PIQ93: Since 3 yrs ago: started living with a (girlfriend/boyfriend) or partner"
label variable piq93d "PIQ93: Since 3 yrs ago: stopped living with a (girlfriend/boyfriend) or partner"
label variable piq93e "PIQ93: Since 3 yrs ago: had a child"
label variable piq94 "PIQ94: current marital status"
label variable piq95 "PIQ95: Are you currently living with a (girlfriend/boyfriend) or partner"
label variable piq96 "PIQ95: Do you currently have a (girlfriend/boyfriend) or partner?"
*Note: maybe question 97 helps identifying people living in the household
label variable piq100 "PIQ100: Family income"
*Note: questions 101-106 are about the source of family income


*SECTION E: ALL SCHOOL-AGE CHILDREN
label variable piq107c "PIQ107c: Have any of your children repeated grade"
label variable piq108c1 "PIQ107c: child 1 repeated grade"
label variable piq108c2 "PIQ107c: child 2 repeated grade"
label variable piq108c3 "PIQ107c: child 3 repeated grade"

label variable piq107f "PIQ107f: Have any of your children received poor grades"
label variable piq108f1 "PIQ107f: child 1 received poor grades"
label variable piq108f2 "PIQ107f: child 2 received poor grades"
label variable piq108f3 "PIQ107f: child 3 received poor grades"

label variable piq109a "PIQ109a: Have any of your children been suspended/expelled"
*label variable piq110a1 "PIQ109a: child 1 been suspended/expelled"
*label variable piq110a2 "PIQ109a: child 2 been suspended/expelled"
*label variable piq110a3 "PIQ109a: child 3 been suspended/expelled"
*note:variable b-g are not in the data


*SECTION I: PARENTAL WELL-BEING
label variable piq161 "PIQ161: How much of the time during the past month have you felt stressed?"
label variable piq174 "PIQ174: Receive NH benefits when the time of eligibility ended?"
label variable piq175 "PIQ175: Had to adjust"

*SECTION K: ECONOMIC WELL-BEING, EXPENDITURES, & STRATEGIES
label variable piq196c "piq196c: do you have: a checkings account"
label variable piq196f "piq196f: do you have: credit card"
label variable piq196h "piq196h: do you have: vehicle"

*SECTION L: WRAP-UP
*label variable piq223 "PIQ223: Is {CHILDA} currently enrolled in school?"







*********************************************************************************************************************************************
*********************************************************************************************************************************************
*******************************************EIGHT-YEAR FOLLOW-UP (F3)*************************************************************************
*********************************************************************************************************************************************

*SECTION A: LIVING ENVIRONMENT
label variable epi1 "EPI1: How long have ypu lived in this neighborhood"
label variable epi2 "EPI2: As a place to live and raise children, would you say your neighborhood is (5 is excellent)"
label variable epi5 "EPI5: Are you living in the same house or apartment as you were three years ago"
label variable epi6 "EPI6: How many times altogether have you moved in the last three years, including your most recent move?"
label variable epi9 "EPI9: How many rooms in the house"
label variable epi10 "EPI10: family owns house? see alternatives in questionnaire"
label variable epi11 "EPI11: How much rent"
label variable epi14 "EPI14: Mortgage payment"

*SECTION B: PARENTAL AND CHILD HEALTH
label variable epi15 "EPI14: Relative to other people your age, would you rate your overall health at the present time as . . .(5=excelent)"
label variable epi18 "EPI18: Do you have any kind of health condition that makes it hard for you to do paid work or limits the work you can generally count on being able to do?"
label variable epi19a "EPI19A: Child has health problems requiring frequent trips to the doctor"
label variable epi19b "EPI19A: Child has behavior that is hard to control"
label variable epi19c "EPI19A: Child has any other health problem"
label variable epi20ao1 "EPI20AO1: Child has health problems requiring frequent trips to the doctor. Child 1"
label variable epi20ao2 "EPI20AO2: Child has health problems requiring frequent trips to the doctor. Child 2"
label variable epi20ao3 "EPI20AO3: Child has health problems requiring frequent trips to the doctor. Child 3"
label variable epi20bo1 "EPI20BO1: Child has behavior that is hard to control. Child 1"
label variable epi20bo2 "EPI20BO2: Child has behavior that is hard to control. Child 2"
label variable epi20bo3 "EPI20BO3: Child has behavior that is hard to control. Child 3"
label variable epi20co1 "EPI20CO1: Child has any other health problem. Child 1"
label variable epi20co2 "EPI20CO2: Child has any other health problem. Child 2"
label variable epi20co3 "EPI20CO3: Child has any other health problem. Child 3"

*SECTION C: EMPLOYMENT
label variable epi33 "EPI33: Are you currently working for pay for an employer at a full-time job (>30 hours)"
label variable epi34 "EPI34: And how about in the last 12 months?"
label variable epi35 "EPI35: Are you currently (also) working for pay for an employer at one or more part-time jobs (<30 hours)"
label variable epi37 "EPI37: If no in Q35, And how about in the last 12 months?"
label variable epi36 "EPI36: How many part-time jobs do you have"
label variable epi38 "EPI38: Doing anything to earn money"
label variable epi39 "EPI39: How about the last 12 months?"
label variable epi50b "EPI50b: At any time during the last year, did you receive: A raise in pay?"
label variable epi54 "EPI54: Hours per week at this job"
label variable epi55u "EPI55U: How much are(were) you paid for this job: Types"
replace epi55u="Hour" if epi55u=="1"
replace epi55u="Week" if epi55u=="2"
replace epi55u="Month" if epi55u=="3"
replace epi55u="Year" if epi55u=="4"

label variable epi55am "EPI55U: How much are(were) you paid for this job"
label variable epi59 "EPI59: When the job or work weve been discussing ended (see categories in questionnaire)"
label variable epi61 "EPI61: Have you been doing anything to find work during the last four weeks?"
label variable epi62 "EPI62: Have you interviewed with any employers or temporary agencies within the last four weeks?"

*SECTION D: HOUSEHOLD COMPOSITION AND INCOME
label variable epi74a "EPI74: Since 3 yrs ago: got married"
label variable epi74b "EPI74: Since 3 yrs ago: got divorced or separated"
label variable epi74c "EPI74: Since 3 yrs ago: started living with a (girlfriend/boyfriend) or partner"
label variable epi74d "EPI74: Since 3 yrs ago: stopped living with a (girlfriend/boyfriend) or partner"
label variable epi74e "EPI74: Since 3 yrs ago: had a child"
label variable epi75 "EPI75: current marital status"
label variable epi76 "EPI76: Are you currently living with a (girlfriend/boyfriend) or partner"
label variable epi77 "EPI77: Do you currently have a (girlfriend/boyfriend) or partner?"
label variable epi81a "EPI81: Family income"
*there is also an epi81b...(?)

*SECTION E: ALL SCHOOL-AGE AND YOUNG-ADULT CHILDREN
label variable epi88c "EPI88c: Have any of your children repeated grade"
label variable epi89co1 "EPI89c: child 1 repeated grade"
label variable epi89co1 "EPI89c: child 2 repeated grade"
label variable epi89co1 "EPI89c: child 3 repeated grade"

label variable epi88f "EPI88f: Have any of your children received poor grades"
label variable epi89fo1 "EPI89f: child 1 received poor grades"
label variable epi89fo2 "EPI89f: child 2 received poor grades"
label variable epi89fo3 "EPI89f: child 3 received poor grades"

label variable epi90a "EPI90a: Have any of your children been suspended/expelled"
label variable epi91ao1 "EPI91a: child 1 been suspended/expelled"
label variable epi91ao2 "EPI91a: child 2 been suspended/expelled"
label variable epi91ao3 "EPI91a: child 3 been suspended/expelled"

label variable epi90b "EPI90b: Have any of your child had to go to juvenile court"
label variable epi91bo1 "EPI91b: Have any of your child had to go to juvenile court: Child 1"
label variable epi91bo2 "EPI91b: Have any of your child had to go to juvenile court: Child 2"
label variable epi91bo3 "EPI91b: Have any of your child had to go to juvenile court: Child 3"

label variable epi90c "EPI90c: Have any of your child had a problem with drugs or alcohol"
label variable epi91co1 "EPI91c: Have any of your child had a problem with drugs or alcohol: Child 1"
label variable epi91co2 "EPI91c: Have any of your child had a problem with drugs or alcohol: Child 2"
label variable epi91co3 "EPI91c: Have any of your child had a problem with drugs or alcohol: Child 3"

label variable epi90d "EPI90d: Have any of your child got into trouble with the police"
label variable epi91do1 "EPI91d: Have any of your child got into trouble with the police: Child 1"
label variable epi91do2 "EPI91d: Have any of your child got into trouble with the police: Child 2"
label variable epi91do3 "EPI91d: Have any of your child got into trouble with the police: Child 3"

label variable epi90e "EPI90e: Have any of your child did something illegal to get money"
label variable epi91eo1 "EPI91e: Have any of your child did something illegal to get money: Child 1"
label variable epi91eo2 "EPI91e: Have any of your child did something illegal to get money: Child 2"
label variable epi91eo3 "EPI91e: Have any of your child did something illegal to get money: Child 3"

*SECTION I: PARENTAL WELL BEING
label variable epi149 "EPI149: How much of the time during the past month have you felt stressed?"

