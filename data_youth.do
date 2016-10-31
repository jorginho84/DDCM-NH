

*Identifiers: sampleid + child uniquely identifies
label variable zboy "CFS CHILD GENDER, 1=BOY 0=GIRL"

label variable child "Child A or B"
label define child_lbl 1 "Child A" 2 "Child B"
label values child child_lbl


/*

*Identifying Child A/B
cq11: probably child A-B. Based only on 913 valid cases.
childab
by comparing the two above: cq11: 1=child A and 2= child b. This in turn is
consistent with the variable "child". So, child=1 (Child A) and 2 (child b).


*AGE OF KIDS
label variable kid1dats "Birthdate, 1st kid (SAS format)"
destring kid1dats, force replace
format kid1dats %td
gen year_birth=yofd(kid1dats)

destring kid2dats, force replace
format kid2dats %td
gen year_birth2=yofd(kid2dats)

destring kid3dats, force replace
format kid3dats %td
gen year_birth3=yofd(kid3dats)


ALso: kidbdat, kidbyr (kid birth year), kidbmo (kid birth month), agechild: child age at f1 interview date


*/

*********************************************************************************************************************************************
*********************************************************************************************************************************************
*******************************************YEAR-TWO FOLLOW-UP (F2)**************************************************************************
*********************************************************************************************************************************************
*********************************************************************************************************************************************

label variable agechild "Child age at f1 interview date"



***********************************CFS PARENTS**********************************************************************************************

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

*Any of your children have been in CC
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

*SECTION F (I ASUME THAT IS 6-12 YEARS OLD, LIKE SECTION G FROM CHILD B)
*note: p112 has to be answered by a child 6-12 years og age. p64 by younger child?). 
label variable p112 "P112: How far would you like to see CHILD A go in school"
label variable p113 "P113: How far do you think will actually CHILD A go in school"


***********************************CFS CHILD AGES 9-12***************************************************************************************

label variable o1a "During the last week, did you: make your bed or put your toys and things away?"
*o8-29 are omitted b/c of copyright

*SECTION C: "MY HOME"
label variable o30 "O30: You think that PCG is perfect"
label variable o31 "O31: You have to keep quiet or leave the house when PCG is at home"
label variable o32 "O32: Your PCG tries to understand your problems and worries"
label variable o33 "O33: Your PCG spends time talking with you"
label variable o34 "O34: You are happy when you are at home"
label variable o35 "O35: You talk over important plans with your PCG"
label variable o36 "O36: Often have good times at home with your PCG"
label variable o38 "O38: You feel that PCG is proud of you"
label variable o40 "O40: You feel close to your PCG"
label variable o41 "O41: Your PCG argues with you a lot"
label variable o44 "O44: Your PCG nags at you"
label variable o46 "O46: Hard to be happy when your PCG is around"
label variable o48 "O48: There is real love and affection for you at home"


*SECTION E: FRIENDS AND INTERESTS
label variable o53 "O53: It's easy for me to make new friends"
label variable o54 "O54: I like to read"
label variable o55 "O54: I have nobody to talk to"
label variable o59 "O59: I like school"
label variable o60 "O60: I have lots of friends"
*items 77-94 omitted due to copyright (they are in the codebook though)

*SECTION G: JOBS AND EDUCATION
label variable o97 "o97: How sure are you that you will go to high school"
label variable o98 "o98: How sure are you that you will finish high school"
label variable o99 "o99: How sure are you that you will go to college"
label variable o100 "o100: How sure are you that you will finish"




***********************************CFS CHILD AGES 6-8***************************************************************************************

*SECTION B: FRIENDS AND INTERESTS
label variable y5 "Y5: It is easy for you to make new friends"
label variable y6 "Y6: Do you like to read"
label variable y11 "Y11: Do you like school"
label variable y12 "Y12: Do you have lots of friends"
*items 29-40 omitted due to copyright (but they are in the codebook)

*SECTION D: "MY HOME"
label variable y41 "Y41: Your PCG spends time talking with you"
label variable y42 "Y42: Does your PCG say things about you that make you feel bad?"
label variable y44 "Y44: Does your PCG argue or yell at you a lot?"
label variable y45 "Y45: Whe you are sad, does your PCG try to make you feel better?"
label variable y46 "Y46: Is your PCG proud of you?"
label variable y47 "Y47: Is your PCG nice to you?"
label variable y48 "Y48: Does your PCG say things about you that make you feel good?"
label variable y49 "Y49: Are you happy when you're at home?"
label variable y50 "Y50: It is hard to get along with your PCG?"
label variable y51 "Y51: It is easy to talk with your PCG about things?"
label variable y52 "Y52: Do you have good times at home with your PCG?"
*items 53-65 omitted due to copyright (they are in the codebook)



*******************************Teachers' report*******************************************
/*How do I know these are from two-year?. Responses to tq1b ( year questionnaire completed)=1997-1998*/
label variable tq4 "TQ4: Classroom size"
label variable tq5 "TQ5: Grade level"

*Classroom Behavior Scale
label variable tcsbs "Classroom: Behavior skills"
label variable tcsis "Classroom: Independent skills"
label variable tcsts "Classroom: Transitional skills"
label variable tcstot "Classroom: total skills"

*SSRS academic subscale: 1=10% lowest, 5=1=% highest
label variable tacad "SSRS: academic (T)"


label variable tq11b "Days absent"


*These variables have 1-5 min-max, and go from a-j (like year 5). Nonetheless, tacad has 417
/*
Confirmed: tacad is based on the sample average of tq17a-j.
*/

label variable tq17a "SSRS: Overall"
label variable tq17b "SSRS: Reading"
label variable tq17c "SSRS: Math"
label variable tq17d "SSRS: Reading, grade expectations"
label variable tq17e "SSRS: Math,grade expectations"
label variable tq17f "SSRS: Motivation"
label variable tq17g "SSRS: Parental encouragement"
label variable tq17h "SSRS: Intellectual functioning"
label variable tq17i "SSRS: Classroom behavior"
label variable tq17j "SSRS: Communication skills"


*********************************************************************************************************************************************
*********************************************************************************************************************************************
*******************************************FIVE-YEAR FOLLOW-UP (F2)**************************************************************************
*********************************************************************************************************************************************
*********************************************************************************************************************************************


******************************Parents' interview (year-5 follow up)*************************************************************************

*SECTION E: ALL SCHOOL-AGE CHILDREN

/*cannot identify child in this variable. can use piq108, but I would not know if these children 
correspond to the ones in the youth database*/
label variable piq107f "In the last 12 months, received poor grades" 
label variable piq112aa "PIQ112: Child care in the last year Child A"
label variable piq112ab "PIQ112: Months in CC. Child A"
label variable piq112ac "PIQ112: How often. Child A"

*SECTION F: CHILD CARE -- CHILDA/B
*child care during school year
label variable piq113aa "PIQ113a: by someone 16 years if age or younger"
label variable piq113ba "PIQ113b: by an adult at your home"
label variable piq113ca "PIQ113c: by an adult in their home"
label variable piq113da "PIQ113d: in a CC center, before or after school program, comm center, or HS"
label variable piq113ea "PIQ113e: child's own supervision"
label variable piq113fa "PIQ113f: sibling"
label variable piq113ga "PIQ113g: any other regular I didn't mention"

label variable piq114aa "PIQ114a: by someone 16 years if age or younger: Months"
label variable piq114ba "PIQ114b: by an adult at your home: Months"
label variable piq114ca "PIQ114c: by an adult in their home: Months"
label variable piq114da "PIQ114d: in a CC center, before or after school program, comm center, or HS: Months"
label variable piq114ea "PIQ114e: child's own supervision: Months"
label variable piq114fa "PIQ114f: sibling: Months"
label variable piq114ga "PIQ114g: any other regular I didn't mention: Months"

label variable piq115aa "PIQ115a: by someone 16 years if age or younger: How often"
label variable piq115ba "PIQ115b: by an adult at your home: How often"
label variable piq115ca "PIQ115c: by an adult in their home: How often"
label variable piq115da "PIQ115d: in a CC center, before or after school program, comm center, or HS: How often"
label variable piq115ea "PIQ115e: child's own supervision: How often"
label variable piq115fa "PIQ115f: sibling: How often"
label variable piq115ga "PIQ115g: any other regular I didn't mention: How often"

*note: PIQ116-19 ask about the last summer

label variable piq119a "PIQ119a: Did you or anyone else pay for Child A (B) to participate in any of the school arrangements"
*note: there is a piq119x. maybe it's child B?
label variable piq128a "PIQ128a: how much did you, (your [spouse/partner]) or another family member pay for child care counting all of thearrangements you had for all of your children?"
label variable piq128b "PIQ128b: how much did you, (your [spouse/partner])... (categories)"

*SECTION G: EDUCATIONAL PROGRESS -- CHILDA/B
label variable piq139 "PIQ139: School type"
label variable piq140 "PIQ140: Grade"
label variable piq143 "PIQ143: Has Child A changed school in the last three years?"
label variable piq144 "PIQ144: How many times Child A changed school in the last three years?"
label variable piq146a "PIQ146a: How well she/he did in: Reading"
label variable piq146b "PIQ146b: How well she/he did in: Math"
label variable piq146c "PIQ146c: How well she/he did in: Written work"
label variable piq146d "PIQ146d: How well she/he did in: Overall"
label variable piq147 "PIQ147: How far you like to see Child A go in school"
label variable piq148 "PIQ148: How far will Child A actually go in school"
label variable piq149 "PIQ149: What would you settle for"


*Child B: NOT IN THE DATABASE
/*
label variable piq150 "PIQ150: School type"
label variable piq151 "PIQ151: Grade"
label variable piq154 "PIQ154: Has Child A changed school in the last three years?"
label variable piq155 "PIQ155: How many times Child A changed school in the last three years?"
label variable piq157a "PIQ157a: How well she/he did in: Reading"
label variable piq157b "PIQ157b: How well she/he did in: Math"
label variable piq157c "PIQ157c: How well she/he did in: Written work"
label variable piq157d "PIQ157d: How well she/he did in: Overall"
label variable piq158 "PIQ158: How far you like to see Child A go in school"
label variable piq159 "PIQ159: How far will Child A actually go in school"
label variable piq160 "PIQ160: What would you settle for"
*/



*SECTION H: ACTIVITIES, SOCIAL BEHAVIOR, & PARENTING: these are year 5 or 8?
label variable pa2q4a "PA2Q4a: Take Lessons (not sports)"
label variable pa2q4b "PA2Q4b: play sports"
label variable pa2q4f "PA2Q4f: Program to help with school work"
label variable pa2q4g "PA2Q4g: Before- or after school child care"
label variable pa2q4h "PA2Q4h: Participate in any other organized activities"

label variable pa2q8a "PA2Q8A: Approve: taking lessons such as dance and music"
label variable pa2q8b "PA2Q8B: Approve: playing sports with a coach"
label variable pa2q8c "PA2Q8C: Approve: going to clubs or youth groups"
label variable pa2q8d "PA2Q8D: Approve: going to recreation or community centers"
label variable pa2q8e "PA2Q8E: Approve: working for pay away home"
*Note: question 9 seems to be a particular test.
label variable pa2q10a "PA2Q10A: My child seems to be much harder to care for than most"
label variable pa2q10b "PA2Q10B: There are some things my child does that really bother me a lot"
label variable pa2q10c "PA2Q10C: Sometimes I lose patience with my child's demands and questions"
label variable pa2q10d "PA2Q10D: I often feel angry with my child."
label variable pa2q11 "PA2Q11: How much trouble raising the child"
label variable pa2q12a "PA2Q12A: How many times in the past week have you: grounded him?"
label variable pa2q12b "PA2Q12B: How many times in the past week have you: Taken away TV, allowance, other?"
label variable pa2q12c "PA2Q12C: How many times in the past week have you: sent to her room"
label variable pa2q12d "PA2Q12D: How many times in the past week have you: show physical affection"
label variable pa2q12e "PA2Q12E: How many times in the past week have you: spank her"
label variable pa2q12f "PA2Q12F: How many times in the past week have you: Praised your child for doing something worthwhile"
label variable pa2q12g "PA2Q12G: How many times in the past week have you: told another adult something positive"
label variable pa2q12h "PA2Q12H: How many times in the past week have you: threatened to punish your child"
label variable pa2q12i "PA2Q12i: How many times in the past week have you: yelled at or scolded"

label variable pa2q13 "PA2Q13: have you had times when you lost control of your feelings and felt you might hurt your child?"
label variable pa2q17a "PA2Q17A: How often did you: Talk to your child about things that might get {him/her} in trouble"
label variable pa2q17b "PA2Q17B: Enforce rules intended to keep {him/her} from getting involved in problem activities"
label variable pa2q17c "PA2Q17C: Get {him/her} involved in an organized activity that was supervised by an adult?"
label variable pa2q17d "PA2Q17D: Punish or threaten to punish your child for doing things that might lead to problems"
label variable pa2q17e "PA2Q17E: Make sure he or she spent time with family and friends"
label variable pa2q17f "PA2Q17F: Keep him or her at home as much as possible"

label variable pa2q19a "PA2Q19A: How often: Do you praise your child"
label variable pa2q19a "PA2Q19B: Do you and your child talk or play with each other focusing attention on each other for five minutes or more, just for fun"
label variable pa2q19a "PA2Q19C: Do you do something special with child that he or she enjoys"

******************************Youth interview (year-5 follow up) (Ages 9-15)***********************************************************************

*SECTION B: THE FUTURE
label variable yiq45a "YIQ45: How sure are you that you will: Finish high school"
label variable yiq45b "YIQ45: How sure are you that you will: Go to college"
label variable yiq45c "YIQ45: How sure are you that you will: Finish college"
label variable yaq46c "How important is for you to: get married"
label variable yaq46e "How important is for you to: having a safe place to raise your kids"
label variable yaq46d "How important is for you to: having a good job"

*SECTION C: MY HOME
label variable yaq49c "YAQ49: Your PCG tries to understand your problems and worries"
label variable yaq49d "YAQ49: Your PCG spends a lot of time talking to you"
label variable yaq49e "YAQ49: Your are happy when you are at home"
label variable yaq49i "YAQ49: Your PCG is proud of you"
label variable yaq49k "YAQ49: You feel close to him"


*SECTION E: WHAT IF?
label variable yiq55 "YIQ55: Why did the kid get milk all over your back?"
label variable yiq56 "YIQ55: In this story, do you think the kid was"

*SECTION F: FEELINGS
label variable yaq65a "YAQ65: It's easy for you to make new friends"
label variable yaq65f "YAQ65: You feel alone"
label variable yaq65p "YAQ65: You don't have any friends"

*SECTION G: SCHOOL
label variable yaq66 "YAQ66: How good at math are you?"
label variable yaq67 "YAQ67: How good at reading you?"
label variable yaq70 "YAQ70: How well do you expect to do in math this year?"

*SECTION I: WOODCOCK-JOHNSON
label variable raw_scr1 "RAW_SCR1: Raw score: letter-word identification"
label variable raw_scr2 "RAW_SCR2: Raw score: passage comprehension"
label variable raw_scr3 "RAW_SCR3: Raw score: calculation"
label variable raw_scr4 "RAW_SCR4: Raw score: applied problems"

label variable wjss22 "WJSS22: WOODCOCK JOHNSON STANDARD SCORE1:LETTER-"
label variable wjss23 "WJSS23: WOODCOCK JOHNSON STANDARD SCORE2:COMPREH"
label variable wjss24 "WOODCOCK JOHNSON STANDARD SCORE3:CALCULA"
label variable wjss25 "WJSS25: WOODCOCK JOHNSON STANDARD SCORE4:PROBLEM"


*SECTION H: BELIEFS
label variable yaq86 "YAQ86: you expect your work to be a very central part of your life"
label variable yaq86 "YAQ86: you would want to do  your best in your job"

*SECTION I: WOODCOCK JOHNSON
*????

/*
*what about these ones?: I think they are child/youth WSJ scores.
wjwscr1
WJWSCR1: WOODCOCK JOHNSON W SCORE1:LETTER-WORD
WJWSCR2: WOODCOCK JOHNSON W SCORE1:LETTER-WORD
WJWSCR3: WOODCOCK JOHNSON W SCORE3:CALCULATION
WJWSCR4: WOODCOCK JOHNSON W SCORE4:PROBLEMS
WJWTOT: WOODCOCK JOHNSON W ALL 4 SUBTESTS

WJSS22: WOODCOCK JOHNSON STANDARD SCORE1:LETTER-
WJSS23: WOODCOCK JOHNSON STANDARD SCORE2:COMPREH
WJSS24: WOODCOCK JOHNSON STANDARD SCORE3:CALCULA
WJSS25: WOODCOCK JOHNSON STANDARD SCORE4:PROBLEM

they come after variable on non-response inputation...

WTFS24M
wtfs24m

*/



******************************Child Interview (year-5 follow up) (ages 6-8)******************************************************************

*SECTION A: LET'S PRETEND
label variable chq1 "CHQ1: Why did the kid get milk all over your back?"

*SECTION C: MY HOME
label variable chq19 "CHQ19: Does your PCG spend a lo of time talking to you?"
label variable chq20 "CHQ20: Does your PCG say things about you that make you feel bad?"
label variable chq22 "CHQ22: Does your PCG argue or yell at you a lot?"
label variable chq22 "CHQ24: Is your PCG proud of you?"
label variable chq27 "CHQ27: Are you happy when you are at home?"

*SECTION D: FEELINGS?
label variable chq32 "CHQ32: Is it easy for you to make new friends?"
label variable chq37 "CHQ32: Do you feel alone?"

*SECTION E: SCHOOL
label variable chq48 "CHQ48: How good at math are you?"
label variable chq49 "CHQ49: How good at reading english are you?"
label variable chq58 "CHQ58: How well do you expect to do in math this year?"


*SECTION F: WOODCOCK-JOHNSON (???)
label variable chscore1 "CHSCORE1: WCJ Lttr Wrd Ident Raw score,F2"
label variable chscore2 "CHSCORE2: WCJ Pssge Comp Raw Score,F2"
label variable chscore3 "CHSCORE3: WCJ Calculation Raw Score,F2"
label variable chscore4 "CHSCORE4: WCJ Applied Prblms Raw Score,F2"



*******************************Teachers' report*******************************************************************************************

/*How do I know these are from two-year?. Responses to T21FL00 T2:1ST TCHER SURVEY-FALL, 2000 */
label variable t2q5mc "T2Q5MC: grade student is in"

*1: not at all. 5: very
label variable t2q11a "T2:HOW SURE CHILD WILL FINISH HIGH SCOOL"
label variable t2q11b "T2:HOW SURE CHILD WILL GO TO COLLEGE"
label variable t2q11c "T2:HOW SURE CHILD WILL FINISH COLLEGE"

label variable t2q12a "T2:PERCENT OF DAYS STUDENT IS ABSENT"
label variable t2q12b "T2:PERCENT OF DAYS STUDENT IS TARDY"

*MOck reports cards: 1= below average, 5= excellent.
label variable t2q16a "T2:STUDENT READING PERFORMANCE"
label variable t2q16b "T2:STUDENT ORAL LANGUAGE PERFORMANCE"
label variable t2q16c "T2:STUDENT WRITTEN LANGUAGE PERFORMANE"
label variable t2q16d "T2:STUDENT MATH PERFORMANCE"
label variable t2q16e "T2:STUDENT SOCIAL STUDIES PERFORMANCE"
label variable t2q16f "T2:STUDENT SCIENCE PERFORMANCE"


*SSRS academic subscale 1: lowest 10%, 5: highest 10%" I am omitting d-e:READING COMP TO GRADE EXPECT	
label variable t2q17a "T2:COMPAR OVERALL ACADEMIC PERFORMANC"
label variable t2q17b "T2:COMPAR READING ABILITY"
label variable t2q17c "T2:COMPAR MATH ABILITY"
label variable t2q17d "T2:READING GRADE EXPECTATIONS"
label variable t2q17e "T2:math GRADE EXPECTATIONS"
label variable t2q17f "T2:COMPAR OVERALL MOTIVATION"
label variable t2q17g "T2:COMPAR PARENTAL ENCOURAGEMENT"
label variable t2q17h "T2:COMPAR INTELLECTUAL FUNCTIONING"
label variable t2q17i "T2:COMPAR OVERALL CLASS BEHAVIOR"
label variable t2q17j "T2:COMPAR COMMUNICATION SKILLS"

label variable etsq13a "OVERALL ACADEM COMP TO CLASS-CAT,F3"
label variable etsq13b "READING COMP TO CLASS-CAT,F3"
label variable etsq13c "MATH COMP TO CLASS-CAT,F3"
label variable etsq13d "READING COMP TO GRADE EXPECT-CAT,F3"
label variable etsq13e "MATH COMP TO GRADE EXPECT-CAT,F3"
label variable etsq13f "MOTIVATION TO SUCCEED-CAT,F3"
label variable etsq13g "PARENT ENCOURAGEMENT-CAT,F3"
label variable etsq13h "INTELECT FUNCTIONING-CAT,F3"
label variable etsq13i "CLASSROOM BEHAVIOR-CAT,F3"
label variable etsq13j "ORAL CUMMINICATION-CAT,F3"


*School adjustment scale (classroom behavior scale)
label variable bhvscaf2 "BHVSCAF2: MEAN SCORE:CLASS BEHAVIOR SUBSCALE"
label variable trnscaf2 "TRNSCAF2: MEAN SCORE: TRANS SKILLS SUBSCALE"
label variable indscaf2 "INDSCAF2: MEAN SCORE: IND SEATWORK SKILLS SUBSCALE"
label variable clascaf2 "CLASCAF2: MEAN SCORE:CLASS SKILLS SCALE"




/*

ACDSCAF2: MEAN SCORE:SUM /NONMISS ACAD SUBSCALE

*/





*********************************************************************************************************************************************
*********************************************************************************************************************************************
*******************************************EIGHT-YEAR FOLLOW-UP (F3)**************************************************************************
*********************************************************************************************************************************************
*********************************************************************************************************************************************


******************************Parents' interview (year-8 follow up)*************************************************************************

*SECTION F: ACTIVITIES AND CHILD CARE (CHILD A+B)
label variable epi96 "EPI96: date of birth"

label variable epi97a "EPI97: Taking lessons such as dance or music"
label variable epi97b "EPI97: Playing sports with coach/instructor"
label variable epi97a "EPI97: Going o clubs"
label variable epi97a "EPI97: Going to recreation community"
label variable epi97a "EPI97: Working for pay away from home"
label variable epi97a "EPI97: Taking part in religious services or classes"

label variable epi102 "EPI102: How much money in a typical month in out-of-school activities"

*only for children<12
label variable epi104a "EPI104: In the past, how often was the child cared by an adult"
label variable epi104b "EPI104: In the past, how often was the child on his own without an adult"
label variable epi104c "EPI104: In the past, how often was the child cared for by someone <16 years old"
label variable epi105 "epi105: how much did you, (your [spouse/partner]) or another family member pay for child care counting all of the arrangements you had for all of your children?"

*Activitirs: (old section H)

*SECTION G: EDUCATIONAL PROGRESS-CHILD A/B

*Child A+B: there is no epi135 (the equivalent for child B). therefore, these are already merged for each child
label variable epi117 "EPI117: School type"
label variable epi118 "EPI118: Grade"
label variable epi119 "EPI119: vouchers?"
label variable epi121 "EPI121: Has Child A changed school in the last three years?"
label variable epi122 "EPI122: How many times Child A changed school in the last three years?"
label variable epi124a "EPI124a: How well she/he did in: Reading"
label variable epi124b "EPI124b: How well she/he did in: Math"
label variable epi124c "EPI124c: How well she/he did in: Written work"
label variable epi124d "EPI124d: How well she/he did in: Overall"
label variable epi125 "EPI125: How far you like to see Child A go in school"
label variable epi126 "EPI126: How far will Child A actually go in school"
label variable epi127 "EPI127: What would you settle for"

*Child B: not in the database (CHild B is also contained in the previous one)
/*
label variable epi128 "EPI128: School type"
label variable epi129 "EPI129: Grade"
label variable epi130 "EPI130: vouchers?"
label variable epi132 "EPI132: Has Child A changed school in the last three years?"
label variable epi133 "EPI133: How many times Child A changed school in the last three years?"
label variable epi135a "EPI135a: How well she/he did in: Reading"
label variable epi135b "EPI135b: How well she/he did in: Math"
label variable epi135c "EPI135c: How well she/he did in: Written work"
label variable epi135d "EPI135d: How well she/he did in: Overall"
label variable epi136 "EPI136: How far you like to see Child A go in school"
label variable epi137 "EPI137: How far will Child A actually go in school"
label variable epi138 "EPI138: What would you settle for"

*/

*SECTION H ACTIVITIES AND CHILD CARE (CHILD B). CONTAINED IN SECTION F

******************************Youth interview (year-8 follow up)*************************************************************************

*SECTION B: THE FUTURE
label variable eyiq47a "EYIQ47A: How sure are you that you will: finish high school"
label variable eyiq47b "EYIQ47B: How sure are you that you will: go to college"
label variable eyiq47c "EYIQ47C: How sure are you that you will: finish college"

*SECTION E: WHAT IF
label variable eyiq59a "EYIQ59a: Why did the kid get milk all over your back?"

*SECTION G: SCHOOL

*SECTION I: WOODCOCK JOHNSON (I THINK, BASED ON THE YEAR-5 FOLLOW UP SECTION)
*note: unlike year-5, there are only 3 raw scores...??

label variable ewjwscr1 "WOODCOCK JOHNSON W SCORE1:LETTER-WORD"
label variable ewjwscr2 "WOODCOCK JOHNSON W SCORE2:COMPREHENSN"
label variable ewjwscr4 "WOODCOCK JOHNSON W SCORE4:PROBLEMS"
label variable ewjwtot "EWJWTOT: WOODCOCK JOHNSON W 3 SUBTESTS"/*this is just a sum*/

*Standard scores
label variable ewjss22 "EWJSS22: WJ STANDARD SCORE1:LETTER-WORD LABEL"
label variable ewjss25 "EWJSS25: WJ STANDARD SCORE4: PROBLEMS"
label variable ewjsstot "EWJSSTOT: WJ AVG. LETTER, COMP, PROBLMS"

/*
label variable ewjss22 "EWJSS22: WJ STANDARD SCORE1:LETTER-WORD LABEL"
label variable ewjss25 "EWJSS25: WJ STANDARD SCORE4: PROBLEMS"
label variable ewjsstot "EWJSSTOT: WJ AVG. LETTER, COMP, PROBLMS"

label variable utwsbrf3 "UTWSBRF3: Mean:WJ Broad Reading stand sc, w3"
label variable utwwbrf3 "UTWWBRF3: WJ W SCORES--Broad READING,F3"

label variable eyiraws1 "EYIRAWS1:Raw score: letter-word identification" 
label variable eyiraws2 "EYIRAWS1:Raw score: passage comprehension" 
label variable eyiraws3 "EYIRAWS1:Raw score: calculation" 


*apparently, this has the right scale

*/




/*
*The following must correspond to Woodcock johnson, year-8 follow-up. 

EWJWSCR1: WOODCOCK JOHNSON W SCORE1:LETTER-WORD

ewjwscr2
EWJWSCR2: 96MO: WOODCOCK JOHNSON W SCORE2:COMPREHENSN

EWJWSCR4: 96MO: WOODCOCK JOHNSON W SCORE4:PROBLEMS

EWJWTOT: 96MO: WOODCOCK JOHNSON W 3 SUBTESTS

EWJSS22: 96MO: WJ STANDARD SCORE1:LETTER-WORD LABEL

EWJSS25: 96MO: WJ STANDARD SCORE4:PROBLEMS

UTWSBRF3: Mean:WJ Broad Reading stand sc, w3

UTWWBRF3: WJ W SCORES--Broad READING,F3

EWJSSTOT: 96MO: WJ AVG. LETTER, COMP, PROBLMS

*/



*******************************Teachers' report*******************************************

*Teachers' expectations
label variable etsq9a "WILL CHD FINISH HS-CAT,F3"
label variable etsq9b  "WILL SURE CHD GO TO COLLEGE-CAT,F3"
label variable etsq9c "TS: WILL CHD FINISH COLLEGE-CAT,F3"


*Teachers mock cards
label variable etsq12a "READING PERFORMANCE-CAT,F3" 
label variable etsq12b "ORAL LANG PERFORMANCE-CAT,F3" 
label variable etsq12c "WRITTEN LANG PERFORMANCE-CAT,F3" 
label variable etsq12d "MATH PERFORMANCE-CAT,F3" 
label variable etsq12e "SOC STUD PERFORMANCE-CAT,F3" 
label variable etsq12f "SCIENCE PERFORMANCE-CAT,F3" 

*Teachers SSRS
label variable etsq13a "OVERALL ACADEM COMP TO CLASS-CAT,F3"
label variable etsq13b "READING COMP TO CLASS-CAT,F3"
label variable etsq13c "MATH COMP TO CLASS-CAT,F3"
label variable etsq13d "READING COMP TO GRADE EXPECT-CAT,F3"
label variable etsq13e "MATH COMP TO GRADE EXPECT-CAT,F3"
label variable etsq13f "MOTIVATION TO SUCCEED-CAT,F3"
label variable etsq13g "PARENT ENCOURAGEMENT-CAT,F3"
label variable etsq13h "INTELECT FUNCTIONING-CAT,F3"
label variable etsq13i "CLASSROOM BEHAVIOR-CAT,F3"
label variable etsq13j "ORAL CUMMINICATION-CAT,F3"

*Teachers CBS
label variable bhvscaf3 "Mean Score: Classroom Behavior Skills Subscale, F3"
label variable trnscaf3 "Mean Score: Transitional Skills Subscale, F3"
label variable indscaf3 "Mean Score: Independent Seatwork Skills Subscale, F3"
label variable clascaf3 "Mean Score: Classroom Skills Total, F3"

