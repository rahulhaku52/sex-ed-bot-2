import os, json, requests, time, random
from io import BytesIO

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

if not BOT_TOKEN or not CHANNEL_ID:
    print("❌ BOT_TOKEN or CHANNEL_ID not set!")
    exit(1)

INDEX_FILE = "last_index.json"
REPLY_MARKUP = {
    "inline_keyboard": [
        [{"text": "🔗 Join Our List", "url": "https://t.me/addlist/57pQLQQl0Oo1MDk9"}]
    ]
}

# ---------- পোস্ট লোড ----------
with open('posts.json', 'r', encoding='utf-8') as f:
    posts = json.load(f)

total = len(posts)
print(f"📊 Total posts: {total}")
if total == 0:
    print("❌ No posts!")
    exit(1)

# ---------- ইনডেক্স ----------
try:
    with open(INDEX_FILE, 'r') as f:
        last_index = json.load(f)
    print(f"📂 Read last_index: {last_index}")
except:
    last_index = total
    print(f"📂 No file. Start from end. Set: {total}")

next_index = (last_index - 1) % total
print(f"➡️ Next index: {next_index} (0-{total-1})")

post = posts[next_index]
caption = post.get('text', '')
print(f"📝 Caption: {caption[:60]}...")

# ---------- ইমেজ জেনারেশন (একেবারে আলাদা প্রতিবার) ----------
def build_image_prompt():
    """পোস্টের টেক্সট না দেখে, সম্পূর্ণ র‌্যান্ডম Adult Vibe ইমেজ প্রম্পট তৈরি করবে"""
    # আপনার পছন্দের দৃশ্য তালিকা
    scenes = [
        # শাড়ি ওঠানো, প্যান্টি দেখা
        "A Bangladeshi woman in a thin saree, saree lifted above her navel, revealing her panty, shy smile, village courtyard",
        "A woman in a saree, bending forward to pick something, saree falls revealing her panty line, back view, outdoor",
        "A woman in a wet saree, saree clinging to her body, transparent fabric, panty outline visible, rainy background",

        # ব্লাউজ খোলা, ব্রা দেখা
        "A woman in a tight blouse, top buttons open, one side of bra peeking out, saree loosely draped, bedroom",
        "A woman sitting on a bed, blouse partially unbuttoned, bra cups visible, seductive expression, dim lighting",
        "A woman in a blouse and petticoat, blouse unhooked from behind, bra strap fallen, mirror reflection",

        # শুধু ব্রা ও প্যান্টি
        "A woman in a bra and panty, standing by the window, morning light, curvy figure, romantic mood",
        "A woman in a lacy bra and panty, lying on a bed, one hand touching her navel, soft focus",

        # শর্টস ও ছোট টপ
        "A Bangladeshi girl wearing tiny shorts and a crop top, sitting on a chair, legs crossed, village house background",
        "A woman in shorts and a tank top, bending to pick up a bucket, side view, outdoor, natural lighting",

        # নাইটিতে
        "A woman in a thin nighty, lying on a bed, one strap fallen, moody lighting, sensual atmosphere",
        "A woman in a nighty, standing near a window, rain outside, nighty slightly transparent from the light"
    ]

    # র‌্যান্ডম দৃশ্য বাছাই
    scene = random.choice(scenes)

    # র‌্যান্ডম রঙ প্যালেট
    colors = random.choice([
        "warm colors, gold and red tones",
        "cool colors, blue and silver tones",
        "pastel colors, soft pink and lavender",
        "earthy tones, brown and green"
    ])

    # র‌্যান্ডম আলো ও আবহাওয়া
    lighting = random.choice([
        "sunset light, golden hour glow",
        "night time, lantern light, warm shadows",
        "rainy evening, wet textures, soft focus",
        "morning light, soft and dreamy"
    ])

    # র‌্যান্ডম পোজ ও বিবরণ
    pose_details = random.choice([
        "looking directly at camera, intense eyes",
        "looking away, shy expression",
        "half-closed eyes, lips slightly parted",
        "smiling gently, relaxed posture"
    ])

    # ইউনিক সল্ট – এটাই ক্যাশ ভাঙবে
    unique_salt = f"uid:{random.randint(100000, 999999)}_{random.randint(100000, 999999)}"

    prompt = f"{scene}, {colors}, {lighting}, {pose_details}, cinematic, photorealistic, adult vibe, no nudity, tasteful, {unique_salt}"
    return prompt[:400]

def fetch_pollinations_image(prompt):
    encoded = requests.utils.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}"
    print(f"🎨 Pollinations URL: {url}")

    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=60)
            print(f"   Attempt {attempt+1}: status {resp.status_code}, length {len(resp.content)}")
            if resp.status_code == 200 and 'image' in resp.headers.get('content-type', ''):
                return BytesIO(resp.content).read()  # bytes
            elif resp.status_code == 503:
                print(f"   Server busy, retrying in 8 sec...")
                time.sleep(8)
            else:
                print(f"   Unexpected status/content-type. Body: {resp.text[:100]}")
                break
        except Exception as e:
            print(f"   Error: {e}")
            break
    return None

print("🎨 Generating image with Pollinations...")
prompt = build_image_prompt()
image_bytes = fetch_pollinations_image(prompt)

# ---------- টেলিগ্রামে পাঠানো ----------
send_photo_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
send_msg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

if image_bytes:
    # ছবি পাঠাই
    files = {"photo": ("image.jpg", image_bytes, "image/jpeg")}
    data = {
        "chat_id": CHANNEL_ID,
        "caption": caption,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(REPLY_MARKUP)
    }
    try:
        resp = requests.post(send_photo_url, files=files, data=data, timeout=30).json()
        if resp.get('ok'):
            print("✅ Image + caption posted!")
        else:
            print(f"❌ sendPhoto error: {resp}")
            # fallback টেক্সট
            resp2 = requests.post(send_msg_url, json={
                "chat_id": CHANNEL_ID,
                "text": caption,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
                "reply_markup": REPLY_MARKUP
            }, timeout=15).json()
            print("✅ Text fallback posted" if resp2.get('ok') else f"❌ Text fallback error: {resp2}")
    except Exception as e:
        print(f"❌ Exception sending photo: {e}")
        # fallback
        requests.post(send_msg_url, json={
            "chat_id": CHANNEL_ID,
            "text": caption,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": REPLY_MARKUP
        }, timeout=15)
else:
    # ছবি নেই – শুধু টেক্সট
    print("⚠️ Image generation failed – sending text only.")
    resp = requests.post(send_msg_url, json={
        "chat_id": CHANNEL_ID,
        "text": caption,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": REPLY_MARKUP
    }, timeout=15).json()
    if resp.get('ok'):
        print("✅ Text posted!")
    else:
        print(f"❌ Text error: {resp}")
        exit(1)

# ---------- ইনডেক্স সংরক্ষণ ----------
with open(INDEX_FILE, 'w') as f:
    json.dump(next_index, f)
print(f"💾 Saved index: {next_index}")
