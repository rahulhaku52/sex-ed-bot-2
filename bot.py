import os, json, requests, time

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

if not BOT_TOKEN or not CHANNEL_ID:
    print("❌ BOT_TOKEN or CHANNEL_ID not set!")
    exit(1)

INDEX_FILE = "last_index.json"

# পোস্ট লোড
with open('posts.json', 'r', encoding='utf-8') as f:
    posts = json.load(f)

total = len(posts)
print(f"📊 Total posts: {total}")

if total == 0:
    print("❌ No posts!")
    exit(1)

# last_index পড়া
try:
    with open(INDEX_FILE, 'r') as f:
        last_index = json.load(f)
    print(f"📂 Read last_index: {last_index}")
except:
    last_index = total
    print(f"📂 No file. Start from end. Set: {total}")

# শেষ থেকে শুরু
next_index = (last_index - 1) % total
print(f"➡️ Next index: {next_index} (0-{total-1})")

# পোস্ট
post = posts[next_index]
text = post.get('text', '')
print(f"📝 Post: {text[:60]}...")

# ইমেজ প্রম্পট তৈরি (প্রথম ১৫০ ক্যারেক্টার + সিনেমাটিক কিওয়ার্ড)
prompt_text = text[:150].strip()
prompt = f"{prompt_text}, romantic, couple, sensual, cinematic, realistic, attractive"
print(f"🖼️ Image prompt (first 100 chars): {prompt[:100]}...")

# Pollinations.ai দিয়ে ইমেজ জেনারেট (ফ্রি, কোনো API Key লাগবে না)
def generate_image(prompt):
    encoded = requests.utils.quote(prompt[:200])
    url = f"https://image.pollinations.ai/prompt/{encoded}"
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.content
            elif resp.status_code == 503:
                print(f"⏳ Pollinations busy, retry {attempt+1}/3")
                time.sleep(5)
            else:
                print(f"❌ Pollinations error {resp.status_code}")
                break
        except Exception as e:
            print(f"❌ Pollinations exception: {e}")
            break
    return None

image_bytes = generate_image(prompt)

# ইনলাইন বাটন (টেক্সট এবং ফটো উভয়ের জন্যই)
reply_markup = {
    "inline_keyboard": [
        [{"text": "🔗 Join Our List", "url": "https://t.me/addlist/57pQLQQl0Oo1MDk9"}]
    ]
}

# ছবি পাঠানোর চেষ্টা
photo_sent = False
if image_bytes:
    # sendPhoto API
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    files = {'photo': ('image.jpg', image_bytes, 'image/jpeg')}
    data = {
        'chat_id': CHANNEL_ID,
        'caption': text[:1024],  # ক্যাপশন (টেলিগ্রাম সীমা)
        'parse_mode': 'HTML',
        'reply_markup': json.dumps(reply_markup)
    }
    try:
        resp = requests.post(url, files=files, data=data, timeout=30)
        res = resp.json()
        if res.get('ok'):
            print("✅ Photo sent!")
            photo_sent = True
        else:
            print(f"❌ Photo send error: {res}")
    except Exception as e:
        print(f"❌ Photo send exception: {e}")

# ছবি না গেলে টেক্সট-only
if not photo_sent:
    print("📝 Falling back to text-only...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, json={
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": reply_markup
    }, timeout=15).json()

    if res.get('ok'):
        print("✅ Text posted!")
    else:
        print(f"❌ Telegram error: {res}")
        exit(1)

# ইনডেক্স সেভ
with open(INDEX_FILE, 'w') as f:
    json.dump(next_index, f)
print(f"💾 Saved index: {next_index}")
