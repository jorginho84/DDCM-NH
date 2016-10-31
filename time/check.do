*checking if everything is right

/*
everything is right, except that jobs have an end date even though the respondant
says that he is still in the job. I think this marks the date of the interview.
how should I consider this spell? (it is censored). 
After this date, I should eliminate this observation from the sample. If I could find
the date of the interview I could prove this assumption and fix it: CONFIRMED

*/

*this guy has a end date for job #4, but says he is still employed when answered
list emp1996* emp1997* start* end* r*atjf1 date_survey if _n==2


list emp1996* emp1997* emp1998* start* end* r*atjf1 date_survey if _n==4

*this one has a date_survey<date_end.
list emp1996* emp1997* emp1998* start* end* r*atjf1 date_survey if _n==100



list emp1996* emp1997* emp1998* start* end* r*atjf1 date_survey if _n==151


list emp1996* emp1997* emp1998* start* end* r*atjf1 date_survey if _n==290
