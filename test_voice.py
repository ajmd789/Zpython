import os
import time
import subprocess
import threading
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 配置
BASE_URL = "http://127.0.0.1:8000/voice-room"
LOG_FILE = "logs/voice.log"

def start_django_server():
    print("Starting Django server (with built-in STUN)...")
    # 使用 Daphne 启动 ASGI 应用
    daphne_path = os.path.join(sys.prefix, "bin", "daphne")
    subprocess.Popen([daphne_path, "-p", "8000", "zproject.asgi:application"])

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 使用本地的用户数据目录，防止访问系统目录导致崩溃
    user_data_dir = os.path.join(os.getcwd(), "chrome_user_data", str(time.time()))
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    
    # 尝试在当前目录下安装驱动，避免权限问题
    driver_path = os.path.join(os.getcwd(), "drivers")
    os.makedirs(driver_path, exist_ok=True)
    
    try:
        # 指定缓存路径到当前项目下的 drivers 目录
        os.environ['WDM_LOCAL'] = '1'
        os.environ['WDM_CACHE_DIR'] = driver_path
        service = Service(ChromeDriverManager().install())
    except Exception as e:
        print(f"Warning: Failed to install chromedriver via manager: {e}")
        print("Trying default chromedriver from PATH...")
        service = Service() # Try default
        
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def cleanup_processes():
    print("Cleaning up old processes...")
    # 简单的清理命令，可能会失败如果无权限，但不影响后续
    try:
        # stun_server 现在由 django 启动，所以只需要杀 daphne (或者 python 如果是 runserver)
        subprocess.run("pkill -f 'daphne'", shell=True)
        # 仍然尝试杀一下独立的 stun_server 防止有残留
        subprocess.run("pkill -f 'stun_server.py'", shell=True)
    except Exception:
        pass
    time.sleep(1)

def run_test():
    cleanup_processes()
    
    # 1. 启动服务 (Django 会自动启动 STUN)
    start_django_server()
    
    # 等待服务启动
    time.sleep(5)
    
    print("Opening Browser 1 (User A)...")
    driver1 = setup_driver()
    driver1.get(BASE_URL)
    
    print("Opening Browser 2 (User B)...")
    driver2 = setup_driver()
    driver2.get(BASE_URL)
    
    time.sleep(2)
    
    # User A Join Slot 0
    print("User A joining...")
    buttons1 = driver1.find_elements(By.TAG_NAME, "button")
    for btn in buttons1:
        if "上麦" in btn.text:
            btn.click()
            break
            
    time.sleep(2)
    
    # User B Join Slot 1
    print("User B joining...")
    buttons2 = driver2.find_elements(By.TAG_NAME, "button")
    for btn in buttons2:
        if "上麦" in btn.text:
            btn.click()
            break
            
    time.sleep(5)
    
    # 验证连接状态
    try:
        status1 = driver1.find_element(By.ID, "connection-status").text
        status2 = driver2.find_element(By.ID, "connection-status").text
        print(f"User A Status: {status1}")
        print(f"User B Status: {status2}")
        
        # 打印浏览器控制台日志
        print("--- Browser 1 Console Logs ---")
        for entry in driver1.get_log('browser'):
            print(entry)
        print("--- Browser 2 Console Logs ---")
        for entry in driver2.get_log('browser'):
            print(entry)
            
        if "已连接" in status1 and "已连接" in status2:
            print("SUCCESS: Both users connected!")
        else:
            print("WARNING: Connection might not be fully established (check logs).")
            
    except Exception as e:
        print(f"Error checking status: {e}")
        
    # 检查日志文件
    if os.path.exists(LOG_FILE):
        print(f"Log file {LOG_FILE} exists.")
        with open(LOG_FILE, 'r') as f:
            logs = f.read()
            if logs:
                print("Log file has content.")
                # print(logs[-500:]) # 打印最后500字符
            else:
                print("WARNING: Log file is empty.")
    else:
        print(f"ERROR: Log file {LOG_FILE} not found.")

    # 保持一会以便观察
    time.sleep(5)
    
    driver1.quit()
    driver2.quit()
    
    print("Test finished. Note: Servers are still running in background processes.")
    print("You may need to manually kill python/daphne processes if running locally.")

if __name__ == "__main__":
    run_test()
