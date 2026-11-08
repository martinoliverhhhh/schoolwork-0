import subprocess, time, os

profile_path = r'C:\Users\12559\Documents\profile.do'
script = '''cd "c:/Users/12559/Desktop/社会调查实践"
noisily {
    do "汤晋欢+24307090021_代码.do"
}
'''
with open(profile_path, 'w', encoding='utf-8') as f:
    f.write(script)
with open(r'C:\Users\12559\profile.do', 'w', encoding='utf-8') as f:
    f.write(script)

log_file = r'c:\Users\12559\Desktop\社会调查实践\汤晋欢+24307090021_运行日志.log'
if os.path.exists(log_file):
    os.remove(log_file)

p = subprocess.Popen([r'C:\Users\12559\Desktop\stata182025.lnk'], shell=True)
print('Launched Stata, executing 汤晋欢+24307090021_代码.do ...')

# Wait for completion: Stata should exit on its own after log close & exit, clear
for i in range(60):
    time.sleep(1)
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if "数据处理与模型运行完毕" in content or "closed on:" in content:
            print(f'Execution completed successfully in {i+1}s! Log size: {os.path.getsize(log_file)} bytes')
            break
else:
    print('Wait loop finished. Checking log status...')

# Clean profile.do
with open(profile_path, 'w', encoding='utf-8') as f:
    f.write('// clean\n')
with open(r'C:\Users\12559\profile.do', 'w', encoding='utf-8') as f:
    f.write('// clean\n')

print("Profile.do cleaned.")
