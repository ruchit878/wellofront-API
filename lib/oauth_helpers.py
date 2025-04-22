# lib/oauth_helpers.py

import os
import requests
from jose import jwt

def exchange_code_to_tokens(code: str, verifier: str, redirect_uri: str) -> dict:
    # MOCK branch for local dev
    if os.getenv("DEV_MOCK_OAUTH") == "1":
        return {
            "access_token":  "FAKE_ACCESS_TOKEN",
            "refresh_token": "FAKE_REFRESH_TOKEN",
            "expires_in":    3600,
            "email":         "you@example.com",
            "name":          "Local Dev User",
            "picture":       None,
        }

    # REAL exchange
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "grant_type":    "authorization_code",
        "code":          code,
        "client_id":     os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri":  redirect_uri,
        "code_verifier": verifier,
    }
    resp = requests.post(token_url, data=data)
    print(">>> TOKEN EXCHANGE STATUS:", resp.status_code, resp.text)
    resp.raise_for_status()
    tokens = resp.json()
    id_info = jwt.get_unverified_claims(tokens["id_token"])
    return {
        "access_token":  tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "expires_in":    tokens["expires_in"],
        "email":         id_info.get("email"),
        "name":          id_info.get("name"),
        "picture":       id_info.get("picture"),
    }