import discord
from discord.ext import commands
from flask import Flask, request, jsonify, render_template_string
import threading, os, json, asyncio
from interface import HTML_PAGE

# --- قاعدة البيانات ---
DATA_FILE = "settings.json"
def load_db():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return []

def save_db(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False)

db = load_db()

# --- البوت ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    content = message.content.lower()
    for rule in db:
        for word in rule['words']:
            if word.lower() in content:
                await handle_violation(message, rule)
                return
    await bot.process_commands(message)

async def handle_violation(message, rule):
    user = message.author
    
    # 1. الحذف
    if rule['delete']['active']:
        wait = int(rule['delete']['timer'])
        await asyncio.sleep(wait)
        try: await message.delete()
        except: pass

    # 2. الرد
    if rule['reply']['active']:
        wait_r = int(rule['reply']['timer'])
        await asyncio.sleep(wait_r)
        msg = rule['reply']['msg']
        if rule['reply']['loc'] == 'dm':
            try: await user.send(msg)
            except: pass
        else:
            await message.channel.send(f"{user.mention} {msg}")

    # 3. الأوامر (Ban, Mute, Kick)
    if rule['command']['active']:
        cmd = rule['command']
        reason = cmd['reason']
        try:
            if cmd['type'] == 'ban':
                await user.ban(reason=reason)
            elif cmd['type'] == 'kick':
                await user.kick(reason=reason)
            elif cmd['type'] == 'mute':
                import datetime
                dur = datetime.timedelta(minutes=int(cmd['dur']))
                await user.timeout(dur, reason=reason)
        except Exception as e: print(f"Command Error: {e}")

# --- سيرفر الويب ---
app = Flask(__name__)

@app.route('/')
def index(): return render_template_string(HTML_PAGE)

@app.route('/api/rules')
def get_rules(): return jsonify(db)

@app.route('/api/save', methods=['POST'])
def save_rule():
    global db
    new_rule = request.json
    db = [r for r in db if r['id'] != new_rule['id']] # إزالة القديم إذا كان تعديلاً
    db.append(new_rule)
    save_db(db)
    return jsonify({"status": "ok"})

@app.route('/api/delete/<id>', methods=['DELETE'])
def delete_rule(id):
    global db
    db = [r for r in db if str(r['id']) != str(id)]
    save_db(db)
    return jsonify({"status": "ok"})

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.run(os.getenv('DISCORD_TOKEN'))
