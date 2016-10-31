/*
this do-file computs the impact of new hope on year's 2 skills measures
it runs 2 files. Both of them are needed to generate one set of table .

-skills_y2.do: computes the impact with no control variables
-skills_y2_c.do: computes the impact with control variables


*/

global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"

do "$codes/skills/skills_y2.do"
do "$codes/skills/skills_y2_c.do"

do "$codes/skills/skills_y5.do"
do "$codes/skills/skills_y5_c.do"

do "$codes/skills/skills_y8.do"
do "$codes/skills/skills_y8_c.do"
