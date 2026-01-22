import discord
from discord.ext import commands
from flask import Flask, request, render_template_string
import threading
import os
import asyncio

# --- إعدادات البوت ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# قاعدة بيانات وهمية (يُفضل ربطها بـ MongoDB لاحقاً للحفاظ على البيانات)
data = {
    "banned_words": {}, # "word": {"action": "ban", "duration": 7, "delete_days": 1, "reply_type": "none"}
    "logs": []
}

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    content = message.content.lower()
    for word, config in data["banned_words"].items():
        if word in content:
            await execute_advanced_action(message, word, config)
            return
    await bot.process_commands(message)

async def execute_advanced_action(message, word, config):
    user = message.author
    action = config['action']
    reason = "مخالفة القوانين (نظام الرقابة التلقائي)"

    try:
        if action == "delete":
            await message.delete()
        
        elif action == "ban":
            # delete_messages_days: كم يوم نمسح من رسائله السابقة
            await user.ban(reason=reason, delete_message_days=int(config.get('delete_days', 0)))
        
        elif action == "timeout":
            import datetime
            duration = datetime.timedelta(minutes=int(config.get('duration', 10)))
            await user.timeout(duration, reason=reason)
            await message.delete()

        elif action == "reply":
            msg_text = config.get('reply_text', 'محتوى مخالف')
            if config['reply_type'] == "private":
                await user.send(msg_text)
            elif config['reply_type'] == "ephemeral":
                # الرسائل المخفية تعمل فقط مع الـ Slash Commands عادةً، هنا سنرد ونحذف
                await message.channel.send(f"{user.mention} {msg_text}", delete_after=5)
            else:
                await message.reply(msg_text)
            await message.delete()

    except Exception as e:
        print(f"Error: {e}")

# --- إعدادات الموقع (Dashboard) ---
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl">
<head><title>لوحة تحكم البوت الرقابي</title></head>
<body>
    <h1>إضافة كلمة محظورة</h1>
    <form method="POST" action="/add">
        الكلمة: <input type="text" name="word" required><br>
        الإجراء: 
        <select name="action">
            <option value="delete">Delete</option>
            <option value="ban">Ban</option>
            <option value="timeout">Timeout</option>
            <option value="reply">Reply</option>
        </select><br>
        (إذا اخترت Ban/Timeout) المدة بالدقائق: <input type="number" name="duration" value="0"><br>
        (إذا اخترت Reply) نص الرد أو الرابط: <input type="text" name="reply_text"><br>
        نوع الرد: 
        <select name="reply_type">
            <option value="public">عام</option>
            <option value="private">خاص</option>
            <option value="ephemeral">مخفي (تلقائي الحذف)</option>
        </select><br>
        <button type="submit">إضافة</button>
    </form>
    <hr>
    <h2>الكلمات الحالية:</h2>
    <ul>
        {% for word, cfg in words.items() %}
            <li>{{ word }} - {{ cfg.action }} <a href="/remove/{{ word }}"> [حذف] </a></li>
        {% endfor %}
    </ul>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, words=data["banned_words"])

@app.route('/add', methods=['POST'])
def add_word():
    word = request.form.get('word').lower()
    data["banned_words"][word] = {
        "action": request.form.get('action'),
        "duration": request.form.get('duration'),
        "reply_text": request.form.get('reply_text'),
        "reply_type": request.form.get('reply_type')
    }
    return "تمت الإضافة بنجاح! <a href='/'>العودة</a>"

@app.route('/remove/<word>')
def remove_word(word):
    if word in data["banned_words"]:
        del data["banned_words"][word]
    return "تم الحذف! <a href='/'>العودة</a>"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# تشغيل الموقع والبوت معاً
if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.start()
    bot.run(os.getenv('DISCORD_TOKEN'))
