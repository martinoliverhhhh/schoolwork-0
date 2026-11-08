import subprocess, time, os

profile_path = r'C:\Users\12559\Documents\profile.do'
script = '''cd "c:/Users/12559/Desktop/社会调查实践"
capture log close
noisily {
    log using "test_iscogen.log", replace text
    di "=== TESTING ISCOGEN ON CGSS2023 ==="
    use "c:/Users/12559/Desktop/CGSS2023/CGSS2023.dta", clear
    keep if isurban == 1 | isurban == 2
    count
    recode isco08f (-5/-1 = .)
    iscogen f_isei = isei(isco08f), from(isco08)
    sum f_isei, detail
    log close
}
exit, clear
'''
with open(profile_path, 'w', encoding='utf-8') as f:
    f.write(script)
with open(r'C:\Users\12559\profile.do', 'w', encoding='utf-8') as f:
    f.write(script)

log_file = r'c:\Users\12559\Desktop\社会调查实践\test_iscogen.log'
if os.path.exists(log_file):
    os.remove(log_file)

p = subprocess.Popen([r'C:\Users\12559\Desktop\stata182025.lnk'], shell=True)
print('Launched Stata, waiting for log...')
for i in range(30):
    time.sleep(1)
    if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
        time.sleep(2) # wait for close
        print(f'Log found after {i+1}s, size: {os.path.getsize(log_file)}')
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            print(f.read())
        break
else:
    print('Timeout waiting for log.')
    if os.path.exists(log_file):
        print(f'Log exists but size is: {os.path.getsize(log_file)}')

with open(profile_path, 'w', encoding='utf-8') as f:
    f.write('// clean\n')
with open(r'C:\Users\12559\profile.do', 'w', encoding='utf-8') as f:
    f.write('// clean\n')
