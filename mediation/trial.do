qui xi: reg etsq13a i.p_assign if d_y8==1
scalar ate_y8=_b[_Ip_assign_2]

*Regression: can't do fixed effects b/c there is no variation in random assignment within family.
xi: reg etsq13a /*t2q17a*/ i.p_assign /*log_income_y6_8 hours_y6_8*/ /* Current inputs
*/ d_CC  /*log_income_y3_5 hours_y3_5 */ log_income_y1_2 hours_y1_2 /* Past inputs
*/ age_ra i.gender i.ethnic i.marital i.cat_educ  if d_y8==1/*X's*/


*Year 5
xi: reg t2q17a tq17a i.p_assign /*log_income_y3_5 hours_y3_5*/ /* Current inputs
*/ d_CC  log_income_y1_2 hours_y1_2 /* Past inputs
*/ age_ra i.gender i.ethnic i.marital i.cat_educ  if d_y5==1/*X's*/
