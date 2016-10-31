use "$databases/Youth_original2.dta", clear

*labels
qui: do "$codes/data_youth.do"
keep  sampleid child p_assign zboy agechild  tq17a t2q17a etsq13a 

count if tq17a!=.

gen age_cat=agechild<=7
replace age_cat=. if agechild==.

table age_cat, c(count tq17a count t2q17a count etsq13a)


xi: reg skills_y2 hours_y2 d_HS

xi: reg skills_y2 hours_y2 d_CC

xi: reg skills_y5 hours_y5 

xi: reg skills_y8 hours_y8 
