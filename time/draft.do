
forvalues x=5/15{
	local y = `x'-1 /*getting the right time for emp*/
	replace hours`x'=0 if emp`y'==0
}
