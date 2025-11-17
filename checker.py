
import imaplib
import email
from email.header import decode_header
import json
import os
from pathlib import Path
from typing import List

import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASS = os.getenv("IMAP_PASS")

CHAT_IDS_FILE = Path("chat_ids.json")
STATE_FILE = Path("state.json")


def load_chat_ids() -> List[int]:
    if CHAT_IDS_FILE.exists():
        try:
            return json.loads(CHAT_IDS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def send_to_all_chats(text: str):
    chat_ids = load_chat_ids()
    if not TELEGRAM_BOT_TOKEN or not chat_ids:
        return

    for cid in chat_ids:
        try:
            requests.post(TELEGRAM_API_URL, data={"chat_id": cid, "text": text})
        except Exception:
            continue


def check_github_notifications(state):
    if not (GITHUB_TOKEN and GITHUB_USERNAME):
        return state

    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    url = "https://api.github.com/notifications"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except Exception:
        return state

    if resp.status_code != 200:
        return state

    data = resp.json()
    last_ids = set(state.get("github_notif_ids", []))
    new_ids = []

    for n in data:
        nid = n.get("id")
        if nid and nid not in last_ids:
            repo = n.get("repository", {}).get("full_name", "repo")
            subject = n.get("subject", {}).get("title", "")
            notif_type = n.get("subject", {}).get("type", "")
            text = f"🐙 Yangi GitHub notification:\nRepo: {repo}\nTuri: {notif_type}\nSarlavha: {subject}"
            send_to_all_chats(text)
            new_ids.append(nid)

    state["github_notif_ids"] = list(last_ids.union(new_ids))
    return state


def decode_mime_words(s):
    decoded = decode_header(s)
    return "".join(
        str(t[0], t[1] or "utf-8") if isinstance(t[0], bytes) else str(t[0])
        for t in decoded
    )


def check_email_notifications(state):
    if not (IMAP_HOST and IMAP_USER and IMAP_PASS):
        return state

    last_uids = set(state.get("email_uids", []))
    new_uids = []

    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST)
        mail.login(IMAP_USER, IMAP_PASS)
        mail.select("INBOX")
    except Exception:
        return state

    try:
        status, data = mail.search(None, "ALL")
    except Exception:
        mail.logout()
        return state

    if status != "OK":
        mail.logout()
        return state

    ids = data[0].split()
    ids = ids[-50:]

    for msg_id in ids:
        if msg_id in last_uids:
            continue

        res, msg_data = mail.fetch(msg_id, "(RFC822)")
        if res != "OK":
            continue

        msg = email.message_from_bytes(msg_data[0][1])
        subject = decode_mime_words(msg.get("Subject", ""))
        from_ = decode_mime_words(msg.get("From", ""))

        if "upwork.com" in from_.lower() or "upwork" in subject.lower():
            text = f"💼 Yangi Upwork/email xabari:\nFrom: {from_}\nSubject: {subject}"
            send_to_all_chats(text)
        elif "github.com" in from_.lower():
            text = f"🐙 Yangi GitHub email xabari:\nFrom: {from_}\nSubject: {subject}"
            send_to_all_chats(text)

        new_uids.append(msg_id.decode())

    mail.logout()

    last_uids_str = {str(uid) for uid in last_uids}
    state["email_uids"] = list(last_uids_str.union(new_uids))
    return state


def main():
    state = load_state()
    state = check_github_notifications(state)
    state = check_email_notifications(state)
    save_state(state)


if __name__ == "__main__":
    main()
