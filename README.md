# المسبحة الإلكترونية (Flask)

تطبيق Python/Flask لإنشاء صدقة جارية (مسبحة) لمتوفى: عدّاد مشترك بين الزوار، عدد المسبّحين، رابط خاص لكل صفحة، وتصميم أخضر.
الصفحة الأولى (`/tasbih/1`) جاهزة: والدة الزميلة خلادي راضية، بإنشاء د. بدر الدين أمينة.

## التشغيل محلياً
    python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python app.py        # http://127.0.0.1:5000/tasbih/1

## الرفع على GitHub
    git init && git add . && git commit -m "Masbaha app"
    git branch -M main
    git remote add origin https://github.com/USERNAME/masbaha.git
    git push -u origin main

> GitHub Pages لا يشغّل Python. GitHub هنا لحفظ الكود فقط، والاستضافة تكون في الخطوة التالية.

## النشر (اختر واحداً)
**PythonAnywhere (الأسهل، والبيانات تبقى محفوظة):**
1. أنشئ حساباً مجانياً، ثم Bash console: `git clone https://github.com/USERNAME/masbaha.git`
2. `pip install --user flask`
3. تبويب Web ← Add a new web app ← Flask ← وجّه ملف WSGI إلى `app` في `masbaha/app.py`.

**Render:** New Web Service من مستودع GitHub، Build: `pip install -r requirements.txt`، Start: `gunicorn app:app`.
القرص المجاني يُمسح عند إعادة التشغيل؛ أضف Persistent Disk واضبط `DB_PATH=/data/tasbih.db`.
