import os, json, requests, time

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

if not BOT_TOKEN or not CHANNEL_ID:
    print("❌ BOT_TOKEN or CHANNEL_ID not set!")
    exit(1)

# ---------- ইমেজ জেনারেশন ----------
prompt = "A couple in saree, romantic, cinematic, realistic, attractive"
encoded = requests.utils.quote(prompt[:200])
url = f"https://image.pollinations.ai/prompt/{encoded}"

print(f"🖼️ Image URL: {url}")

for attempt in range(3):
    try:
        resp = requests.get(url, timeout=30)
        print(f"🔍 Status: {resp.status_code}")
        print(f"🔍 Content-Type: {resp.headers.get('content-type')}")
        print(f"🔍 Content-Length: {len(resp.content)} bytes")

        if resp.status_code == 200 and 'image' in resp.headers.get('content-type', ''):
            # ইমেজ পাঠানোর চেষ্টা
            files = {'photo': ('image.jpg', resp.content, 'image/jpeg')}
            data = {
                'chat_id': CHANNEL_ID,
                'caption': "🧪 Test image from Pollinations",
                'parse_mode': 'HTML'
            }
            send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            send_resp = requests.post(send_url, files=files, data=data, timeout=30).json()
            print(f"📤 SendPhoto response: {send_resp}")
            if send_resp.get('ok'):
                print("✅ Image sent to Telegram!")
            else:
                print(f"❌ Telegram error: {send_resp}")
            exit(0)
        elif resp.status_code == 503:
            print(f"⏳ Pollinations busy, retry {attempt+1}/3")
            time.sleep(5)
        else:
            print(f"❌ Pollinations failed with status {resp.status_code}")
            print(f"❌ Response body: {resp.text[:200]}")
            break
    except Exception as e:
        print(f"❌ Exception: {e}")
        break

print("❌ Image generation completely failed. Sending text instead...")

# টেক্সট-অনলি পাঠানো
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
res = requests.post(url, json={
    "chat_id": CHANNEL_ID,
    "text": "🧪 Test image failed, but text works!",
    "parse_mode": "HTML"
}, timeout=15).json()
print(f"📤 Text response: {res}")
