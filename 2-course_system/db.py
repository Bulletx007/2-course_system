# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูล  ★★★ นิสิตเขียน SQL ในไฟล์นี้ ★★★
#  มองหาคำว่า  # TODO  ทุกฟังก์ชัน — ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
# ============================================================
import mysql.connector
import config


def get_connection():
    return mysql.connector.connect(
        host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD,
        database=config.DB_NAME, port=config.DB_PORT)


def run_query(sql, params=None):
    """รัน SELECT คืนผลเป็น list ของ dict"""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute(sql, params or ()); rows = cur.fetchall()
    cur.close(); conn.close(); return rows


def run_command(sql, params=None):
    """รัน INSERT / UPDATE / DELETE แล้ว commit"""
    conn = get_connection(); cur = conn.cursor()
    cur.execute(sql, params or ()); conn.commit()
    out = {"new_id": cur.lastrowid, "affected": cur.rowcount}
    cur.close(); conn.close(); return out


def _todo(name):
    raise NotImplementedError(f"TODO: ยังไม่ได้เขียนฟังก์ชัน {name} ใน db.py")


# ---------- ผู้เรียน (learner) ----------
def search_learners(filters):
    """ค้นหา ผู้เรียน ตามเงื่อนไข (name, email)
    คำใบ้: เริ่มจาก sql = "SELECT * FROM learner WHERE 1=1"
    แล้วต่อเงื่อนไขเฉพาะ filter ที่มีค่า (ข้อความใช้ LIKE %s, อื่น ๆ ใช้ = %s)"""
    sql = "SELECT * FROM learner WHERE 1=1"
    params = []
    if filters.get("name"):
        sql += " AND name LIKE %s"
        params.append(f"%{filters['name']}%")
    if filters.get("email"):
        sql += " AND email LIKE %s"
        params.append(f"%{filters['email']}%")
    return run_query(sql, params)

def get_learner(learner_id):
    """ดึง ผู้เรียน 1 รายการตาม learner_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    sql = "SELECT * FROM learner WHERE learner_id = %s"
    rows = run_query(sql, (learner_id,))
    return rows[0] if rows else None


def create_learner(data):
    """เพิ่ม ผู้เรียน ใหม่ — ตรวจสอบและใส่วันที่สมัครอัตโนมัติถ้าไม่ได้ระบุ"""
    sql = "INSERT INTO learner (name, email, join_date, member_tier) VALUES (%s, %s, COALESCE(%s, CURDATE()), %s)"
    params = (
        data.get("name"), 
        data.get("email"), 
        data.get("join_date") or None, 
        data.get("member_tier", "normal")
    )
    return run_command(sql, params)


def update_learner(learner_id, data):
    """แก้ไข ผู้เรียน ตาม learner_id — ตรวจสอบและคงค่า join_date เดิมไว้ถ้าไม่ได้ส่งค่ามาใหม่"""
    new_join_date = data.get("join_date")
    
    # [แก้ไข]: เช็คใน Python ว่าถ้าไม่ได้ส่ง join_date มา ให้ดึงค่าวันที่เดิมจากฐานข้อมูลมาใช้ต่อ ป้องกัน Error 1093 ของ MySQL
    if not new_join_date:
        existing = get_learner(learner_id)
        if existing and existing.get("join_date"):
            new_join_date = existing["join_date"]
        else:
            import datetime
            new_join_date = datetime.date.today()

    sql = """
        UPDATE learner 
        SET name = %s, email = %s, join_date = %s, member_tier = %s 
        WHERE learner_id = %s
    """
    params = (
        data.get("name"), 
        data.get("email"), 
        new_join_date, 
        data.get("member_tier", "normal"), 
        learner_id
    )
    return run_command(sql, params)

def delete_learner(learner_id):
    """ลบ ผู้เรียน ตาม learner_id"""
    sql = "DELETE FROM learner WHERE learner_id = %s"
    return run_command(sql, (learner_id,))


# ---------- คอร์ส (course) ----------
def search_courses(filters):
    """ค้นหา คอร์ส ตามเงื่อนไข (title, category)"""
    sql = "SELECT * FROM course WHERE 1=1"
    params = []
    if filters.get("title"):
        sql += " AND title LIKE %s"
        params.append(f"%{filters['title']}%")
    if filters.get("category"):
        sql += " AND category = %s"
        params.append(filters["category"])
    return run_query(sql, params)


def get_course(course_id):
    """ดึง คอร์ส 1 รายการตาม course_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    sql = "SELECT * FROM course WHERE course_id = %s"
    rows = run_query(sql, (course_id,))
    return rows[0] if rows else None


def create_course(data):
    """เพิ่ม คอร์ส ใหม่ — data มีคีย์: title, category, price, prerequisite_id"""
    sql = "INSERT INTO course (title, category, price, seat_limit, prerequisite_id) VALUES (%s, %s, %s, %s, %s)"
    params = (
        data.get("title"),
        data.get("category"),
        data.get("price"),
        data.get("seat_limit", 50),
        data.get("prerequisite_id") or None
    )
    return run_command(sql, params)

def update_course(course_id, data):
    """แก้ไข คอร์ส ตาม course_id"""
    sql = "UPDATE course SET title = %s, category = %s, price = %s, seat_limit = %s, prerequisite_id = %s WHERE course_id = %s"
    params = (
        data.get("title"),
        data.get("category"),
        data.get("price"),
        data.get("seat_limit", 50),
        data.get("prerequisite_id") or None,
        course_id
    )
    return run_command(sql, params)

def delete_course(course_id):
    """ลบ คอร์ส ตาม course_id"""
    sql = "DELETE FROM course WHERE course_id = %s"
    return run_command(sql, (course_id,))


# ---------- การลงทะเบียน (enrollment) ----------
def search_enrollments(filters):
    """ค้นหา การลงทะเบียน ตามเงื่อนไข (learner_id, course_id, status)"""
    sql = "SELECT * FROM enrollment WHERE 1=1"
    params = []
    if filters.get("learner_id"):
        sql += " AND learner_id = %s"
        params.append(filters["learner_id"])
    if filters.get("course_id"):
        sql += " AND course_id = %s"
        params.append(filters["course_id"])
    if filters.get("status"):
        sql += " AND status = %s"
        params.append(filters["status"])
    return run_query(sql, params)

def get_enrollment(enroll_id):
    """ดึง การลงทะเบียน 1 รายการตาม enroll_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    sql = "SELECT * FROM enrollment WHERE enroll_id = %s"
    rows = run_query(sql, (enroll_id,))
    return rows[0] if rows else None


def create_enrollment(data):
    """เพิ่ม การลงทะเบียน ใหม่ — แปลง promo_code เป็น promo_id, คำนวณราคา, และปล่อย enroll_date ให้ใช้ค่าปัจจุบันอัตโนมัติ"""
    learner_id = data.get("learner_id")
    course_id = data.get("course_id")
    promo_code = data.get("promo_code")
    status = data.get("status", "active")
    
    if not learner_id or not course_id:
        raise ValueError("กรุณาระบุรหัสผู้เรียนและรหัสคอร์สให้ครบถ้วน")

    course_rows = run_query("SELECT price FROM course WHERE course_id = %s", (course_id,))
    if not course_rows:
        raise ValueError("ไม่พบรหัสคอร์สนี้ในระบบ")
    base_price = float(course_rows[0]["price"])
    
    promo_id = None
    discount_pct = 0
    
    if promo_code:
        promo_rows = run_query("SELECT promo_id, discount_pct FROM promotion WHERE promo_code = %s", (promo_code,))
        if promo_rows:
            promo_id = promo_rows[0]["promo_id"]
            discount_pct = float(promo_rows[0]["discount_pct"])
        else:
            raise ValueError(f"ไม่พบโค้ดโปรโมชัน '{promo_code}' ในระบบ")
            
    paid_amount = base_price - (base_price * discount_pct / 100)
    
    sql = """
        INSERT INTO enrollment (learner_id, course_id, status, paid_amount, promo_id)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (learner_id, course_id, status, paid_amount, promo_id)
    return run_command(sql, params)


def update_enrollment(enroll_id, data):
    """แก้ไข การลงทะเบียน ตาม enroll_id — รองรับการอัปเดตสถานะและคำนวณราคาใหม่ถ้ามีการเปลี่ยนคอร์สหรือโปรโมชัน"""
    learner_id = data.get("learner_id")
    course_id = data.get("course_id")
    promo_code = data.get("promo_code")
    status = data.get("status", "active")
    
    course_rows = run_query("SELECT price FROM course WHERE course_id = %s", (course_id,))
    if not course_rows:
        raise ValueError("ไม่พบรหัสคอร์สนี้ในระบบ")
    base_price = float(course_rows[0]["price"])
    
    promo_id = None
    discount_pct = 0
    
    if promo_code:
        promo_rows = run_query("SELECT promo_id, discount_pct FROM promotion WHERE promo_code = %s", (promo_code,))
        if promo_rows:
            promo_id = promo_rows[0]["promo_id"]
            discount_pct = float(promo_rows[0]["discount_pct"])
        else:
            raise ValueError(f"ไม่พบโค้ดโปรโมชัน '{promo_code}' ในระบบ")
            
    paid_amount = base_price - (base_price * discount_pct / 100)
    
    sql = """
        UPDATE enrollment 
        SET learner_id = %s, course_id = %s, status = %s, paid_amount = %s, promo_id = %s
        WHERE enroll_id = %s
    """
    params = (learner_id, course_id, status, paid_amount, promo_id, enroll_id)
    return run_command(sql, params)

def delete_enrollment(enroll_id):
    """ลบ การลงทะเบียน ตาม enroll_id"""
    sql = "DELETE FROM enrollment WHERE enroll_id = %s"
    return run_command(sql, (enroll_id,))


# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
# ============================================================
def report_summary():
    """ตัวเลขสรุปบนการ์ด dashboard — นับจำนวนข้อมูลทุกตารางรวมถึงบทเรียน"""
    learners = run_query("SELECT COUNT(*) AS cnt FROM learner")[0]["cnt"]
    courses = run_query("SELECT COUNT(*) AS cnt FROM course")[0]["cnt"]
    enrollments = run_query("SELECT COUNT(*) AS cnt FROM enrollment")[0]["cnt"]
    completed = run_query("SELECT COUNT(*) AS cnt FROM enrollment WHERE status='completed'")[0]["cnt"]
    lessons = run_query("SELECT COUNT(*) AS cnt FROM lesson")[0]["cnt"]
    
    return {
        "learners": learners,
        "courses": courses,
        "enrollments": enrollments,
        "completed": completed,
        "lessons": lessons
    }
    

def report_popular_courses():
    """📈 คอร์สยอดนิยม (Most Enrolled)"""
    sql = """
        SELECT c.course_id, c.title, c.category, COUNT(e.learner_id) AS total_students
        FROM course c
        LEFT JOIN enrollment e ON c.course_id = e.course_id
        GROUP BY c.course_id, c.title, c.category
        ORDER BY total_students DESC
        LIMIT 5
    """
    return run_query(sql)

def report_completion_rate():
    """✅ อัตราการเรียนจบต่อคอร์ส (Completion Rate)"""
    sql = """
        SELECT c.course_id, c.title,
               COUNT(e.enroll_id) AS total_enrolled,
               SUM(CASE WHEN e.status = 'completed' THEN 1 ELSE 0 END) AS total_completed,
               ROUND(SUM(CASE WHEN e.status = 'completed' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(e.enroll_id), 0), 2) AS completion_rate
        FROM course c
        LEFT JOIN enrollment e ON c.course_id = e.course_id
        GROUP BY c.course_id, c.title
    """
    return run_query(sql)


def report_course_prerequisites():
    """🔗 คอร์สและวิชาที่ต้องเรียนก่อน (Self-Join)"""
    sql = """
        SELECT c.course_id, c.title AS course_title, c.category,
               pre.course_id AS prerequisite_id, pre.title AS prerequisite_title
        FROM course c
        LEFT JOIN course pre ON c.prerequisite_id = pre.course_id
    """
    return run_query(sql)


# ---------- โปรโมชัน (promotion) ----------
def get_all_promotions():
    return run_query("SELECT * FROM promotion")


# ---------- บทเรียน (lesson) ----------
def get_all_lessons_with_course():
    sql = """
        SELECT l.lesson_id, c.title AS course_title, l.title AS lesson_title, l.seq_no, l.duration_min
        FROM lesson l
        INNER JOIN course c ON l.course_id = c.course_id
        ORDER BY c.course_id, l.seq_no
    """
    return run_query(sql)


def report_promotion_usage():
    """📊 รายงานการใช้งานโปรโมชันและยอดส่วนลด (ปรับปรุงรูปแบบตัวเลขให้สวยงาม)"""
    sql = """
        SELECT p.promo_id, p.promo_code, p.discount_pct, 
               COUNT(e.enroll_id) AS total_used,
               COALESCE(ROUND(SUM(c.price * p.discount_pct / 100), 2), 0.00) AS total_discount_given
        FROM promotion p
        LEFT JOIN enrollment e ON p.promo_id = e.promo_id
        LEFT JOIN course c ON e.course_id = c.course_id
        GROUP BY p.promo_id, p.promo_code, p.discount_pct
        ORDER BY total_used DESC
    """
    return run_query(sql)