cd "c:/Users/12559/Desktop/社会调查实践"
capture log close
log using "test_run.log", replace text
di "=== RUNNING STATA SUCCESSFULLY ==="
di 123 + 456
log close
exit, STATA clear
