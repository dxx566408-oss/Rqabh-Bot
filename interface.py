HTML_PAGE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>نظام الرقابة المتقدم</title>
    <style>
        :root { --primary: #5865F2; --danger: #ed4245; --success: #3ba55c; --bg: #36393f; }
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: var(--bg); color: white; padding: 20px; }
        .container { max-width: 900px; margin: auto; background: #2f3136; padding: 25px; border-radius: 12px; }
        .hidden { display: none; }
        .card { background: #40444b; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #4f545c; }
        input, select, textarea { background: #202225; color: white; border: 1px solid #000; padding: 10px; border-radius: 4px; width: 100%; margin: 5px 0; }
        .btn { cursor: pointer; border: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; transition: 0.2s; margin: 5px; }
        .btn-main { background: var(--primary); color: white; }
        .btn-add { background: var(--success); color: white; width: auto; padding: 5px 15px; }
        .btn-danger { background: var(--danger); color: white; }
        .flex-row { display: flex; gap: 10px; align-items: center; margin-bottom: 10px; }
        .scroll-box { max-height: 150px; overflow-y: auto; background: #2f3136; padding: 10px; border-radius: 5px; }
        .word-tag { background: var(--primary); padding: 5px 10px; border-radius: 15px; font-size: 14px; display: inline-block; margin: 2px; }
    </style>
</head>
<body>
    <div class="container" id="mainPage">
        <h2>🛡️ الكلمات التي تم تعيينها</h2>
        <button class="btn btn-main" onclick="showAddForm()">إضافة كلمة +</button>
        <hr style="border: 0.5px solid #4f545c;">
        <div id="wordsList"></div>
    </div>

    <div class="container hidden" id="addForm">
        <h2 id="formTitle">إعداد رقابة جديدة</h2>
        
        <div class="card">
            <label>الكلمات المستهدفة:</label>
            <div id="wordsInputs">
                <div class="flex-row"><input type="text" class="target-word"><button class="btn btn-add" onclick="addWordInput()">+</button></div>
            </div>
            
            <div class="flex-row">
                <button class="btn btn-main" onclick="toggleBox('channelsBox')">الرومات المفعلة/المعطلة</button>
                <button class="btn btn-main" onclick="toggleBox('rolesBox')">الرتب المفعلة/المعطلة</button>
            </div>

            <div id="channelsBox" class="hidden scroll-box">
                <button onclick="checkAll('chan')">تفعيل الكل</button> | <button onclick="uncheckAll('chan')">تعطيل الكل</button>
                <div id="channelsList"></div>
            </div>
            
            <div id="rolesBox" class="hidden scroll-box">
                <button onclick="checkAll('role')">تفعيل الكل</button> | <button onclick="uncheckAll('role')">تعطيل الكل</button>
                <div id="rolesList"></div>
            </div>
        </div>

        <div class="card">
            <h3>الإجراءات:</h3>
            <div>
                <input type="checkbox" id="doDelete" onchange="toggleFields('deleteFields')"> حذف الرسالة
                <div id="deleteFields" class="hidden">
                    حذف بعد: <select id="delTimer"><option value="0">مباشرة</option><option value="5">5 ثواني</option><option value="60">دقيقة</option></select>
                </div>
            </div>

            <hr>
            <div>
                <input type="checkbox" id="doReply" onchange="toggleFields('replyFields')"> رد
                <div id="replyFields" class="hidden">
                    <textarea id="replyMsg" placeholder="اكتب الرد هنا..."></textarea>
                    الرد في: <select id="replyLoc"><option value="server">السيرفر</option><option value="dm">الخاص</option></select>
                    توقيت الرد: <select id="replyTimer"><option value="0">مباشرة</option><option value="5">5 ثواني</option></select>
                </div>
            </div>

            <hr>
            <div>
                <input type="checkbox" id="doCommand" onchange="toggleFields('commandFields')"> أمر
                <div id="commandFields" class="hidden">
                    النوع: <select id="cmdType"><option value="ban">Ban</option><option value="mute">Mute</option><option value="kick">Kick</option></select>
                    المدة (بالدقائق): <input type="number" id="cmdDur" value="0">
                    السبب: <input type="text" id="cmdReason" value="مخالفة القوانين">
                </div>
            </div>
        </div>

        <button class="btn btn-add" onclick="saveRule()">حفظ</button>
        <button class="btn btn-danger" onclick="hideAddForm()">إلغاء</button>
    </div>

    <script>
        let editingId = null;

        function showAddForm() { 
            document.getElementById('mainPage').classList.add('hidden');
            document.getElementById('addForm').classList.remove('hidden');
            editingId = null;
        }

        function hideAddForm() {
            document.getElementById('mainPage').classList.remove('hidden');
            document.getElementById('addForm').classList.add('hidden');
        }

        function addWordInput() {
            const div = document.createElement('div');
            div.className = 'flex-row';
            div.innerHTML = '<input type="text" class="target-word"><button class="btn btn-danger" onclick="this.parentElement.remove()">-</button>';
            document.getElementById('wordsInputs').appendChild(div);
        }

        function toggleBox(id) { document.getElementById(id).classList.toggle('hidden'); }
        function toggleFields(id) { document.getElementById(id).classList.toggle('hidden'); }

        function saveRule() {
            const words = Array.from(document.querySelectorAll('.target-word')).map(i => i.value).filter(v => v);
            const data = {
                id: editingId || Date.now(),
                words: words,
                delete: { active: document.getElementById('doDelete').checked, timer: document.getElementById('delTimer').value },
                reply: { active: document.getElementById('doReply').checked, msg: document.getElementById('replyMsg').value, loc: document.getElementById('replyLoc').value, timer: document.getElementById('replyTimer').value },
                command: { active: document.getElementById('doCommand').checked, type: document.getElementById('cmdType').value, dur: document.getElementById('cmdDur').value, reason: document.getElementById('cmdReason').value }
            };

            fetch('/api/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            }).then(() => { location.reload(); });
        }

        function loadRules() {
            fetch('/api/rules').then(r => r.json()).then(rules => {
                const list = document.getElementById('wordsList');
                list.innerHTML = '';
                rules.forEach(r => {
                    list.innerHTML += `
                        <div class="card flex-row" style="justify-content: space-between;">
                            <div>${r.words.map(w => `<span class="word-tag">${w}</span>`).join('')}</div>
                            <div>
                                <button class="btn btn-main" onclick="editRule('${r.id}')">تعديل</button>
                                <button class="btn btn-danger" onclick="deleteRule('${r.id}')">حذف</button>
                            </div>
                        </div>`;
                });
            });
        }
        
        function deleteRule(id) { fetch('/api/delete/'+id, {method: 'DELETE'}).then(() => loadRules()); }
        loadRules();
    </script>
</body>
</html>
"""
