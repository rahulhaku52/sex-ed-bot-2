import os, json, requests, subprocess

BOT_TOKEN = os.environ['BOT_TOKEN']
CHANNEL_ID = os.environ['CHANNEL_ID']
INDEX_FILE = "last_index.json"

# পোস্ট লোড
with open('posts.json', 'r', encoding='utf-8') as f:
    posts = json.load(f)

# শেষ ইনডেক্স পড়া
try:
    with open(INDEX_FILE, 'r') as f:
        last_index = json.load(f)
except:
    last_index = len(posts) if posts else 0

# শেষ থেকে শুরু করে উল্টো দিকে
next_index = (last_index - 1) % len(posts) if posts else 0

# পোস্ট সিলেক্ট
post = posts[next_index]
text = post['text']

# ডিবাগ প্রিন্ট
print(f"Last Index: {last_index}")
print(f"Next Index: {next_index}")
print(f"Posting: {text[:50]}")

# টেলিগ্রামে পাঠানো
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
res = requests.post(url, json={
    "chat_id": CHANNEL_ID,
    "text": text,
    "parse_mode": "HTML",
    "disable_web_page_preview": True
}).json()

print("✅ Posted" if res.get('ok') else f"❌ {res}")

# ইনডেক্স আপডেট ও সেভ
with open(INDEX_FILE, 'w') as f:
    json.dump(next_index, f)

# গিট কমিট ও পুশ
try:
    subprocess.run(["git", "config", "user.name", "GitHub Actions"], check=True)
    subprocess.run(["git", "config", "user.email", "actions@github.com"], check=True)
    subprocess.run(["git", "add", INDEX_FILE], check=True)

    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
    if diff.returncode != 0:
        subprocess.run(["git", "commit", "-m", "Update last index"], check=True)
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Index committed and pushed")
    else:
        print("ℹ️  No change in index")
except subprocess.CalledProcessError as e:
    print(f"⚠️ Git error (push may have failed): {e}")
