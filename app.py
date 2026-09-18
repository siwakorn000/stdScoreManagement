from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from supabase import create_client, Client
import os

app = Flask(__name__)
app.secret_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhhYXRzb2luYWRyY3R3eHJxcXRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4OTQ1MDg5NSwiZXhwIjoyMTA1MDI2ODk1fQ.QeCanyTEHMtK4DP4mGnb4orVf0DG5PS4fghN5YOVkUY' # เปลี่ยนเป็นคีย์ของคุณ

# ตั้งค่า Supabase (เอามาจาก API Settings ใน Supabase)
SUPABASE_URL = "https://xaatsoinadrctwxrqqtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhhYXRzb2luYWRyY3R3eHJxcXRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk0NTA4OTUsImV4cCI6MjEwNTAyNjg5NX0.t3nXHNAuzXFRSgGpKIqtfeEyCBdgRSFuFOliA4oKA-s"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.context_processor
def inject_user():
    # ส่งตัวแปร role และ tchName ไปให้ทุกหน้า HTML อัตโนมัติ (ใช้สำหรับ Base Template)
    return dict(role=session.get('role'), tchName=session.get('tchName'))

@app.route('/')
def role_selection():
    return render_template('role.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        tchName = request.form.get('tchName')
        tchPassword = request.form.get('tchPassword')
        
        # ตรวจสอบรหัสผ่านใน Supabase
        response = supabase.table('teacher').select('*').eq('tchName', tchName).eq('tchPassword', tchPassword).execute()
        if len(response.data) > 0:
            session['role'] = 'teacher'
            session['tchName'] = tchName
            return redirect(url_for('index'))
        else:
            return "ชื่อหรือรหัสผ่านไม่ถูกต้อง", 401
    return render_template('login.html')

@app.route('/set_student_role')
def set_student_role():
    session['role'] = 'student'
    return redirect(url_for('index'))

@app.route('/index')
def index():
    if 'role' not in session:
        return redirect(url_for('role_selection'))
    
    return render_template('index.html', active_menu='home')

@app.route('/department/<int:dept_id>')
def department(dept_id):
    if 'role' not in session:
        return redirect(url_for('role_selection'))
        
    level = request.args.get('level', 1, type=int) # ค่าเริ่มต้นคือชั้นปีที่ 1
    
    # ดึงข้อมูลโดยกรองจาก dept_id (สาขา) และ Level (ชั้นปี)
    students_data = supabase.table('student').select('*').eq('dept_id', dept_id).eq('Level', level).execute().data
    subjects_data = supabase.table('subject').select('*').eq('dept_id', dept_id).eq('Level', level).execute().data
        
    return render_template('department.html', 
                           dept_id=dept_id, 
                           level=level, 
                           students=students_data, 
                           subjects=subjects_data,
                           active_menu='table')

@app.route('/settings')
def settings():
    if session.get('role') != 'teacher':
        return redirect(url_for('index'))
        
    teacher_data = supabase.table('teacher').select('*').eq('tchName', session['tchName']).execute().data[0]
    return render_template('settings.html', teacher=teacher_data, active_menu='settings')

@app.route('/api/change_password', methods=['POST'])
def change_password():
    if session.get('role') != 'teacher':
        return jsonify({"success": False, "message": "Unauthorized"}), 403
        
    data = request.json
    new_password = data.get('new_password')
    tchName = session.get('tchName')
    
    supabase.table('teacher').update({"tchPassword": new_password}).eq('tchName', tchName).execute()
    return jsonify({"success": True})

@app.route('/api/update_score', methods=['POST'])
def update_score():
    if session.get('role') != 'teacher':
        return jsonify({"success": False, "message": "Unauthorized"}), 403
        
    data = request.json
    stdId = data.get('stdId')
    input_scores = data.get('scores') # dict ของคะแนนที่เพิ่งกรอก
    
    # 1. ดึงข้อมูลคะแนนเก่าออกมา
    response = supabase.table('student').select('scores').eq('stdId', stdId).execute()
    if not response.data:
        return jsonify({"success": False, "message": "ไม่พบข้อมูลนักศึกษา"}), 404
        
    current_scores = response.data[0].get('scores') or {}
    
    # 2. อัปเดตทับเฉพาะวิชาที่กรอกลงใน current_scores
    for subj_id, new_score in input_scores.items():
        current_scores[subj_id] = new_score
        
    # 3. คำนวณค่าเฉลี่ยใหม่
    valid_scores = [int(v) for v in current_scores.values() if v is not None and str(v).strip() != '']
    total = sum(valid_scores)
    count = len(valid_scores)
    avgSc = total / count if count > 0 else 0
    
    # 4. บันทึกข้อมูล
    supabase.table('student').update({
        "scores": current_scores, 
        "avgSc": avgSc
    }).eq('stdId', stdId).execute()
    
    return jsonify({"success": True})

@app.route('/api/manage_student', methods=['POST'])
def manage_student():
    if session.get('role') != 'teacher': 
        return jsonify({"success": False}), 403
        
    data = request.json
    action = data.get('action')
    
    if action == 'add':
        supabase.table('student').insert({
            "stdId": data.get('stdId'),
            "stdFName": data.get('fname'),
            "stdLName": data.get('lname'),
            "Level": data.get('level'),
            "dept_id": data.get('dept_id'),
            "scores": {},
            "avgSc": 0
        }).execute()
    elif action == 'delete':
        supabase.table('student').delete().eq('stdId', data.get('stdId')).execute()
        
    return jsonify({"success": True})

@app.route('/api/manage_subject', methods=['POST'])
def manage_subject():
    if session.get('role') != 'teacher': 
        return jsonify({"success": False}), 403
        
    data = request.json
    action = data.get('action')
    
    if action == 'add':
        # สร้างรหัสวิชาชั่วคราวให้อัตโนมัติ เช่น d1_l1_ฟิสิกส์
        subj_id = f"d{data.get('dept_id')}_l{data.get('level')}_{data.get('subjName')}"
        supabase.table('subject').insert({
            "subjId": subj_id,
            "subjName": data.get('subjName'),
            "Level": data.get('level'),
            "dept_id": data.get('dept_id')
        }).execute()
    elif action == 'delete':
        supabase.table('subject').delete().eq('subjId', data.get('subjId')).execute()
        
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)