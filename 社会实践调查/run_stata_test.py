import subprocess, time, os

profile_path = r'C:\Users\12559\Documents\profile.do'
script = '''cd "c:/Users/12559/Desktop/社会调查实践"
capture log close
noisily {
    log using "test_stata_works.log", replace text
    di "=== TESTING STATA EXECUTION ==="
    sysuse auto, clear
    sum price mpg weight
    log close
}
exit, clear
'''
with open(profile_path, 'w', encoding='utf-8') as f:
    f.write(script)

with open(r'C:\Users\12559\profile.do', 'w', encoding='utf-8') as f:
    f.write(script)

log_file = r'c:\Users\12559\Desktop\社会调查实践\test_stata_works.log'
if os.path.exists(log_file):
    os.remove(log_file)

p = subprocess.Popen([r'C:\Users\12559\Desktop\stata182025.lnk'], shell=True)
print('Launched Stata shortcut, waiting for log...')
for i in range(15):
    time.sleep(1)
    if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
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
