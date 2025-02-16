import requests

# 定义请求的 URL
url = "http://localhost:5001/agents/acea9ddf-7b3e-4db9-af17-c6ebd31a2571"

# 定义请求头
headers = {
    "Content-Type": "application/json",
    "apikey": "e77fb393-e99c-4b18-8569-c6dde047fdf4"
}

# 定义请求体
data = {
    "user_input": "Hello, how are you?"
}

# 发送 POST 请求
response = requests.post(url, headers=headers, json=data)

# 检查响应状态码
if response.status_code == 200:
    # 打印响应内容
    print("Response:", response.json())
else:
    print(f"Error: {response.status_code}, {response.text}")