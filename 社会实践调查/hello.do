noisily {
    capture log close
    log using "hello_log_test2.log", replace text
    di "HELLO FROM NOISILY!"
    sysuse auto, clear
    sum
    log close
}
exit, clear
