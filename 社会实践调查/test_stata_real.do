cd "c:/Users/12559/Desktop/社会调查实践"
capture log close
log using "test_stata_real.log", replace text
clear all
set more off

use "c:/Users/12559/Desktop/CGSS2023/CGSS2023.dta", clear
count
di "Total obs in CGSS 2023: " r(N)

* Check iscogen
iscogen f_isei = isei(isco08f), from(isco08)
sum f_isei, detail

log close
exit, clear
