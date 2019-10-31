import sys
import pyautogui
import subprocess
import time

sys.path.append("/home/karolina/ipm1920-p1")
sys.path.append("/home/karolina/ipm1920-p1/img")
subprocess.Popen(['python', '../ipm-p1.py'])
time.sleep(2)
for i in range(14):
	pyautogui.press('tab')
pyautogui.press('enter')
