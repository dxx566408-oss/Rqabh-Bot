import discord
from discord.ext import commands
from flask import Flask, request, jsonify, render_template_string
import threading
import os
import datetime
import json
from interface import HTML_PAGE # استيراد الواجهة من الملف الثاني

# --- إدارة البيانات ---
DATA_FILE = "database.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"words": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()

# --- إعدادات البوت ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(message):
    if message.author.bot: return
    content = message.content.lower()
    for word, config in db["words"].items():
        if word in content:
            await process_violation(message, config)
            break
    await bot.process_commands(message)

async def process_violation(message, config):
    user = message.author
    actions = config.get("actions", [])
    
    if "delete" in actions:
        try: await message.delete()
        except: pass

    if "reply" in actions:
        rt = config.get("reply_text", "محتوى مخالف")
        if config.get("reply_type") == "private":
            try: await user.send(rt)
            except: pass
        else:
            await message.channel.send(f"⚠️ {user.mention}: {rt}", delete_after=15)

    if "timeout" in actions:
        try:
            dur = datetime.timedelta(minutes=int(config.get("duration", 10)))
            await user.timeout(dur, reason="رقابة آليّة")
        except: pass

    if "kick" in actions:
        try: await user.kick(reason="رقابة آليّة")
        except: pass

    if "ban" in actions:
        try: await user.ban(delete_message_days=1, reason="رقابة آليّة")
        except: pass

# --- سيرفر الويب ---
app = Flask(__name__)

@app.route('/')
def home(): return render_template_string(HTML_PAGE)

@app.route('/api/list')
def api_list(): return jsonify(db)

@app.route('/api/add', methods=['POST'])
def api_add():
    req = request.json
    db["words"][req['word'].lower()] = {
        "actions": req['actions'],
        "reply_text": req.get('reply_text'),
        "reply_type": req.get('reply_type'),
        "duration": req.get('duration')
    }
    save_data(db)
    return jsonify({"ok": True})

@app.route('/api/delete/<word>', methods=['DELETE'])
def api_delete(word):
    if word in db["words"]:
        del db["words"][word]
        save_data(db)
    return jsonify({"ok": True})

def run_server():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    bot.run(os.getenv('DISCORD_TOKEN'))
