/*This do file builds a 2x2 matrix:

[1,1]= beta from regression
[1,2]= p-value for the test: beta=0
[2,1]= S.E of the beta
[2,2]= 0

This matrix can be saved in an excel file to construct the final table

*/

mat beta_matrix=e(b)
mat variance_matrix=e(V)
test _Ip_assign_2=0
mat pvalue=r(p)
mat results=(beta_matrix[1,1], pvalue\ variance_matrix[1,1]^.5,0)
