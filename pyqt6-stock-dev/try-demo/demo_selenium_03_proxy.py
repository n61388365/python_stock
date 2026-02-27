# 可以抓到 sse 的数据了
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
import time
import pandas as pd

# os.environ['http_proxy'] = 'http://127.0.0.1:7890'
# os.environ['https_proxy'] = 'http://127.0.0.1:7890'

class JsonDecoder:
  def __init__(self, d) -> None:
    print(type(d))  ## <class 'dict'>
    self.__dict__ = d


# 配置（建议先不 headless 测试，确认通了再加）
options = Options()
options.add_argument('--headless=new')  # 测试通过后再开启
options.add_argument('--disable-gpu')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36')

# 启用 performance log（用于捕获网络事件）
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

driver = webdriver.Chrome(options=options)

# 关键：直接打开分时页面（f1.html），这样 Referer、Cookie、wbp2u 等全自动生成
page_url = "https://quote.eastmoney.com/f1.html?newcode=1.600410"
driver.get(page_url)

# 等待页面加载完成 + JS 发起 SSE（通常 3-8 秒）
time.sleep(1)

print("页面已打开，开始监听 SSE 数据推送...")

# 启用 Network CDP
driver.execute_cdp_cmd("Network.enable", {})

def raw_to_dataframe(data_json):
    # Convert data to DataFrame
    df = pd.DataFrame([row.split(',') for row in data_json['data']['details']], 
                    columns=['Time', 'Price', 'Volume', 'Metric', 'Type'])
    # Convert columns to appropriate types
    df['Time'] = df['Time'].map(lambda x: str(x).zfill(6))
    df['Price'] = df['Price'].astype(float)
    df['Volume'] = df['Volume'].astype(int)
    df['Metric'] = df['Metric'].astype(int)
    df['Type'] = df['Type'].astype(str)
    # Convert time from HH:MM:SS to HHMM
    try:
        df['Time'] = df['Time'].str.replace(':', '').astype(int)
    except Exception as e:
        raise ValueError(f"时间格式转换失败: {str(e)}")
    return df

logs = driver.get_log('performance')
for entry in logs:
    try:
        # if 'Network.eventSourceMessageReceived' in entry['message']:
        if 'rc' in entry['message'] and 'code' in entry['message'] and '600410' in entry['message'] and 'Network.eventSourceMessageReceived' in entry['message']:
            message = json.loads(entry['message'])
            requestId = message['message']['params']['requestId']
            print("request id:", requestId)
            data = json.loads(message['message']['params']['data'])
            df_details = raw_to_dataframe(data)
            print(df_details)
    except Exception as e:
        print("I am here waiting for you {}".format(e))

# 监听循环（示例跑 60 秒，你可以改成 while True + 手动 break）
start_time = time.time()
while time.time() - start_time < 60:
    logs = driver.get_log('performance')
    for entry in logs:
        message = json.loads(entry['message'])['message']
        
        # sse capture
        if message['params']['requestId'] == requestId and 'rc' in entry['message']:
            print(json.loads(message['params']['data'])['data'])
    
    time.sleep(3)  # 避免 CPU 过载

print(f"监听结束")
driver.quit()