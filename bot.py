import os, json, requests, subprocess, sys

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

if not BOT_TOKEN or not CHANNEL_ID:
    print("❌ BOT_TOKEN or CHANNEL_ID not set!")
    sys.exit(1)

INDEX_FILE = "last_index.json"

with open('posts.json', 'r', encoding='utf-8') as f:
    posts = json.load(f)

total = len(posts)
print(f"📊 Total posts: {total}")

if total == 0:
    print("❌ No posts in posts.json")
    sys.exit(1)

# last_index.json পড়া
try:
    with open(INDEX_FILE, 'r') as f:
        last_index = json.load(f)
    print(f"📂 Read last_index: {last_index}")
except:
    last_index = total
    print(f"📂 No index file, set to total: {total}")

next_index = (last_index - 1) % total
print(f"➡️ Next index: {next_index} (0-{total-1})")

post = posts[next_index]
text = post.get('text', '')
print(f"📝 Selected text: {text[:80]}...")

# টেলিগ্রামে পাঠানো
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
res = requests.post(url, json={
    "chat_id": CHANNEL_ID,
    "text": text,
    "parse_mode": "HTML",
    "disable_web_page_preview": True
}, timeout=15).json()

if res.get('ok'):
    print("✅ Posted successfully!")
else:
    print(f"❌ Telegram error: {res}")
    sys.exit(1)

# ইনডেক্স সেভ
with open(INDEX_FILE, 'w') as f:
    json.dump(next_index, f)
print(f"💾 Saved next_index: {next_index}")

# গিট কমিট ও পুশ
try:
    subprocess.run(["git", "config", "user.name", "GitHub Actions"], check=True)
    subprocess.run(["git", "config", "user.email", "actions@github.com"], check=True)
    subprocess.run(["git", "add", INDEX_FILE], check=True)

    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
    if diff.returncode != 0:
        subprocess.run(["git", "commit", "-m", f"Update index to {next_index}"], check=True)
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Git pushed!")
    else:
        print("ℹ️  No change to push")
except subprocess.CalledProcessError as e:
    print(f"⚠️ Git error: {e}")
