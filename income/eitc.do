/*This do-file returns scalar values with the EITC (state and fed) by year

x: number of children. y: year

r1_x_y: credit rate (percent)
r2_x_y: phase-out rate
b1_x_y: minimum income for maximum credit
b2_x_y: beginning income for phase-out

state_x_y: rate of fed EITC
min_state_x_1994: in 1994 the minimum between state_x_y*FED_EITC and min_state_x_1994 was paid

*/




***1994***

*1 child
scalar r1_1_1994=26.3/100
scalar r2_1_1994=15.98/100
scalar b1_1_1994=7750
scalar b2_1_1994=11000
scalar state_1_1994=12/100
scalar min_state_1_1994=92

*2 children
scalar r1_2_1994=30/100
scalar r2_2_1994=17.68/100
scalar b1_2_1994=8425
scalar b2_2_1994=11000
scalar state_2_1994=63/100
scalar min_state_2_1994=499

*3 children
scalar state_3_1994=18.8/100
scalar min_state_3_1994=1496

***1995***

*1 child
scalar r1_1_1995=34/100
scalar r2_1_1995=15.98/100
scalar b1_1_1995=6160
scalar b2_1_1995=11290
scalar state_1_1995=4/100

*2 children
scalar r1_2_1995=36/100
scalar r2_2_1995=20.22/100
scalar b1_2_1995=8640
scalar b2_2_1995=11290
scalar state_2_1995=16/100

*3 children
scalar state_3_1995=50/100

***1996***

*1 child
scalar r1_1_1996=34/100
scalar r2_1_1996=15.98/100
scalar b1_1_1996=6330
scalar b2_1_1996=11610
scalar state_1_1996=4/100

*2 children
scalar r1_2_1996=40/100
scalar r2_2_1996=21.06/100
scalar b1_2_1996=8890
scalar b2_2_1996=11610
scalar state_2_1996=14/100

*3 children
scalar state_3_1996=43/100

***1997***

*1 child
scalar r1_1_1997=34/100
scalar r2_1_1997=15.98/100
scalar b1_1_1997=6500
scalar b2_1_1997=11930
scalar state_1_1997=4/100

*2 children
scalar r1_2_1997=40/100
scalar r2_2_1997=21.06/100
scalar b1_2_1997=9140
scalar b2_2_1997=11930
scalar state_2_1997=14/100

*3 children
scalar state_3_1997=43/100

***1998***

*1 child
scalar r1_1_1998=34/100
scalar r2_1_1998=15.98/100
scalar b1_1_1998=6680
scalar b2_1_1998=12260
scalar state_1_1998=4/100

*2 children
scalar r1_2_1998=40/100
scalar r2_2_1998=21.06/100
scalar b1_2_1998=9390
scalar b2_2_1998=12260
scalar state_2_1998=14/100

*3 children
scalar state_3_1998=43/100

***1999***

*1 child
scalar r1_1_1999=34/100
scalar r2_1_1999=15.98/100
scalar b1_1_1999=6800
scalar b2_1_1999=12460
scalar state_1_1999=4/100

*2 children
scalar r1_2_1999=40/100
scalar r2_2_1999=21.06/100
scalar b1_2_1999=9540
scalar b2_2_1999=12460
scalar state_2_1999=14/100

*3 children
scalar state_3_1999=43/100

***2000***

*1 child
scalar r1_1_2000=34/100
scalar r2_1_2000=15.98/100
scalar b1_1_2000=6920
scalar b2_1_2000=12690
scalar state_1_2000=4/100

*2 children
scalar r1_2_2000=40/100
scalar r2_2_2000=21.06/100
scalar b1_2_2000=9720
scalar b2_2_2000=12690
scalar state_2_2000=14/100

*3 children
scalar state_3_2000=43/100

***2001***

*1 child
scalar r1_1_2001=34/100
scalar r2_1_2001=15.98/100
scalar b1_1_2001=7140
scalar b2_1_2001=13090
scalar state_1_2001=4/100

*2 children
scalar r1_2_2001=40/100
scalar r2_2_2001=21.06/100
scalar b1_2_2001=10020
scalar b2_2_2001=13090
scalar state_2_2001=14/100

*3 children
scalar state_3_2001=43/100

***2002***

*1 child
scalar r1_1_2002=34/100
scalar r2_1_2002=15.98/100
scalar b1_1_2002=7370
scalar b2_1_2002=13520
scalar state_1_2002=4/100

*2 children
scalar r1_2_2002=40/100
scalar r2_2_2002=21.06/100
scalar b1_2_2002=10350
scalar b2_2_2002=13520
scalar state_2_2002=14/100

*3 children
scalar state_3_2002=43/100

**Married
scalar b2_1_2002_m = b2_1_2002 + 1000

scalar b2_2_2002_m = b2_2_2002 + 1000

***2003***

*1 child
scalar r1_1_2003=34/100
scalar r2_1_2003=15.98/100
scalar b1_1_2003=7490
scalar b2_1_2003=13730
scalar state_1_2003=4/100

*2 children
scalar r1_2_2003=40/100
scalar r2_2_2003=21.06/100
scalar b1_2_2003=10510
scalar b2_2_2003=13730
scalar state_2_2003=14/100

*3 children
scalar state_3_2003=43/100

*Married
scalar b2_1_2003_m = b2_1_2003 + 1000

scalar b2_2_2003_m = b2_2_2003 + 1000
