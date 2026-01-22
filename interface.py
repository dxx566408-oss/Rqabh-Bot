HTML_PAGE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>لوحة تحكم الرقابة</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #eef2f3; padding: 20px; direction: rtl; }
        .card { max-width: 700px; margin: auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
        h2 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .input-group { margin: 20px 0; }
        input[type="text"], input[type="number"], select { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        .actions-box { background: #f9f9f9; padding: 15px; border-radius: 8px; margin: 15px 0; }
        .checkbox-item { margin: 10px; display: inline-block; cursor: pointer; }
        button { background: #3498db; color: white; border: none; padding: 12px 25px; border-radius: 5px; width: 100%; font-size: 16px; cursor: pointer; transition: 0.3s; }
        button:hover { background: #2980b9; }
        .word-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #eee; }
        .btn-del { background: #e74c3c; width: auto; padding: 5px 15px; font-size: 12px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🛡️ نظام الرقابة الذكي</h2>
        <div class="input-group">
            <label>الكلمة المستهدفة:</label>
            <input type="text" id="word" placeholder="اكتب الكلمة هنا...">
        </div>
        <div class="actions-box">
            <label>الإجراءات المطلوبة:</label><br>
            <div class="checkbox-item"><input type="checkbox" class="act" value="delete"> حذف</div>
            <div class="checkbox-item"><input type="checkbox" class="act" value="reply"> رد</div>
            <div class="checkbox-item"><input type="checkbox" class="act" value="timeout"> تايم آوت</div>
            <div class="checkbox-item"><input type="checkbox" class="act" value="kick"> طرد</div>
            <div class="checkbox-item"><input type="checkbox" class="act" value="ban"> حظر</div>
        </div>
        <div class="input-group">
            <label>نص الرد (أو رابط الصورة/GIF):</label>
            <input type="text" id="replyText">
            <label>مكان الرد:</label>
            <select id="replyType">
                <option value="public">القناة العامة</option>
                <option value="private">الخاص (DM)</option>
            </select>
        </div>
        <div class="input-group">
            <label>المدة (بالدقائق):</label>
            <input type="number" id="duration" value="10">
        </div>
        <button onclick="submitData()">حفظ الكلمة</button>
        <h3>📋 القائمة الحالية</h3>
        <div id="list"></div>
    </div>
    <script>
        function refresh() {
            fetch('/api/list').then(r => r.json()).then(data => {
                const div = document.getElementById('list');
                div.innerHTML = '';
                for (const [w, c] of Object.entries(data.words)) {
                    div.innerHTML += `<div class="word-item">
                        <span><strong>${w}</strong> (${c.actions.join(' + ')})</span>
                        <button class="btn-del" onclick="del('${w}')">إزالة</button>
                    </div>`;
                }
            });
        }
        function submitData() {
            const word = document.getElementById('word').value;
            const actions = Array.from(document.querySelectorAll('.act:checked')).map(i => i.value);
            if(!word) return alert("ادخل الكلمة أولاً");
            fetch('/api/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    word, actions, 
                    reply_text: document.getElementById('replyText').value,
                    reply_type: document.getElementById('replyType').value,
                    duration: document.getElementById('duration').value
                })
            }).then(() => { refresh(); document.getElementById('word').value = ''; });
        }
        function del(w) { fetch('/api/delete/'+w, {method: 'DELETE'}).then(() => refresh()); }
        refresh();
    </script>
</body>
</html>
"""
