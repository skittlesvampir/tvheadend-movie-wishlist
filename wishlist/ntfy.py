#!/usr/bin/python3
import requests
import base64

import tomli

def send_notification(content,warning=False,error=False,image_url=None):
    with open("config.toml", "rb") as f:
        toml_dict = tomli.load(f)
        
    if not toml_dict["ntfy"]["enabled"]:
        return

    headers={}
    if toml_dict["ntfy"]["authenticated"]:
        username = toml_dict["ntfy"]["username"]
        password = toml_dict["ntfy"]["password"]
        login = f"{username}:{password}"
        login_base64 = base64.b64encode(bytes(login, "utf-8")).decode('utf-8')
        headers["Authorization"] = f"Basic {login_base64}"
    
    if warning:
        headers["Tags"] = "warning"
    if error:
        headers["Tags"] = "rotating_light"
    if image_url != None:
        headers["Attach"] = image_url
    
    channel_url = toml_dict["ntfy"]["channel_url"]
    output = requests.post(channel_url,
        data=content.encode(encoding='utf-8'),
        headers=headers
    )
