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

# ইমেজ জেনারেট
def generate_image(prompt):
    try:
        encoded = requests.utils.quote(prompt[:200])
        url = f"https://image.pollinations.ai/prompt/{encoded}"
        for attempt in range(3):
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.content
            elif resp.status_code == 503:
                print(f"⏳ Pollinations busy, retry {attempt+1}/3")
                time.sleep(5)
            else:
                print(f"❌ Pollinations error: {resp.status_code}")
                break
        return None
    except Exception as e:
        print(f"❌ Pollinations exception: {e}")
        return None

prompt = text[:150].strip() + ", romantic, couple, sensual, cinematic, realistic, attractive"
print(f"🖼️ Image prompt: {prompt[:100]}...")

image_bytes = generate_image(prompt)

if image_bytes:
    # ইমেজ পাঠান
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    files = {'photo': ('image.jpg', image_bytes, 'image/jpeg')}
    data = {
        'chat_id': CHANNEL_ID,
        'caption': text[:300] + "\n\n🔗 Join Our List: https://t.me/addlist/57pQLQQl0Oo1MDk9",
        'parse_mode': 'HTML'
    }
    res = requests.post(url, files=files, data=data, timeout=30).json()

    if res.get('ok'):
        print("✅ Photo sent!")
    else:
        print(f"❌ Photo error: {res}")
        image_bytes = None  # টেক্সট-only তে ফ্যালব্যাক

if not image_bytes:
    # ইমেজ না এলে টেক্সট-only
    reply_markup = {
        "inline_keyboard": [
            [{"text": "🔗 Join Our List", "url": "https://t.me/addlist/57pQLQQl0Oo1MDk9"}]
        ]
    }
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

# সেভ
with open(INDEX_FILE, 'w') as f:
    json.dump(next_index, f)
print(f"💾 Saved index: {next_index}")
