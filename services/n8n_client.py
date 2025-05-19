import os
import requests

def ask_n8n(message: str) -> str:
    host = os.getenv("N8N_HOST", "n8n")
    port = os.getenv("N8N_PORT", "5678")
    path = os.getenv("N8N_WEBHOOK_PATH", "chat")
    url = f"http://{host}:{port}/webhook/{path}"
    payload = {"message": message}
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict):
        if "reply" in data:
            return data["reply"]
        if "choices" in data:
            try:
                return data["choices"][0]["message"]["content"]
            except Exception:
                pass
    elif isinstance(data, list) and data:
        item = data[0]
        if isinstance(item, dict):
            if "reply" in item:
                return item["reply"]
            if "json" in item:
                j = item["json"]
                if "reply" in j:
                    return j["reply"]
                if "choices" in j:
                    try:
                        return j["choices"][0]["message"]["content"]
                    except Exception:
                        pass
    return str(data)
