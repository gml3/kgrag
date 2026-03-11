import requests


url = "http://127.0.0.1:8000/embeddings"  # 1226是SSH端口，这里需要使用8000服务端口（请确保已经通过SSH建立了端口转发映射）

payload = {
    "sentences": [
        "这是第一句",
        "这是第二句"
    ]
}

resp = requests.post(
    url,
    headers={"Content-Type": "application/json"},
    json=payload,
    timeout=10
)

if resp.ok:
    data = resp.json()           # { "data": {...上游返回的结果...} }
    print("向量结果:", data["data"])
else:
    print("调用失败:", resp.status_code, resp.text)