import win32com.client
try:
    stata = win32com.client.Dispatch("stata.StataOLEApp")
    print("Stata COM object created:", stata)
    stata.DoCommand("di 12345+67890")
    print("DoCommand executed!")
except Exception as e:
    print("Error:", e)
