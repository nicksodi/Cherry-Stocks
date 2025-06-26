# 3. app/auth_wrapper.py
import json
import hmac
import hashlib
import base64
import time
import urllib.parse
import os
import requests

def generate_signed_url(command_args: dict) -> str:
    SHARED_KEY = os.getenv("WW_SHARED_KEY")
    SECRET_KEY = os.getenv("WW_SECRET_KEY")

    if not SHARED_KEY or not SECRET_KEY:
        raise ValueError("WW_SHARED_KEY and WW_SECRET_KEY must be set.")

    timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    args_json = json.dumps(command_args, separators=(',', ':'))
    sign_input = args_json + "\n" + timestamp
    hmac_digest = hmac.new(SECRET_KEY.encode(), sign_input.encode(), hashlib.sha1).digest()
    signature = base64.b64encode(hmac_digest).decode().replace('\n', '')
    encoded_args = urllib.parse.quote(args_json)

    return (
        f"https://whalewisdom.com/shell/command.json?args={encoded_args}"
        f"&api_shared_key={SHARED_KEY}&api_sig={signature}&timestamp={timestamp}"
    )

def run_signed_query(command_args: dict):
    url = generate_signed_url(command_args)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Error {response.status_code}: {response.text}")
