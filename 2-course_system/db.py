# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูล  ★★★ นิสิตเขียน SQL ในไฟล์นี้ ★★★
#  มองหาคำว่า  # TODO  ทุกฟังก์ชัน — ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
# ============================================================
import mysql.connector
import datetime
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
    """ค้นหา ผู้เรียน ตามเงื่อนไข (name, email)"""
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
    
    if not new_join_date:
        existing = get_learner(learner_id)
        if existing and existing.get("join_date"):
            new_join_date = existing["join_date"]
        else:
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
def _clean_seat_limit(value, default=None):
    """แปลงและตรวจสอบจำนวนที่นั่ง"""
    if value is None or str(value).strip() == "":
        return default
    try:
        seats = int(value)
    except (TypeError, ValueError):
        raise ValueError("จำนวนที่นั่งต้องเป็นตัวเลขจำนวนเต็ม")
    if seats <= 0:
        raise ValueError("จำนวนที่นั่งต้องมากกว่า 0")
    return seats


def _clean_prerequisite(value, course_id=None):
    """ตรวจสอบรหัสวิชาที่ต้องเรียนก่อน"""
    if value is None or str(value).strip() == "":
        return None
    try:
        prereq = int(value)
    except (TypeError, ValueError):
        raise ValueError("รหัสวิชาที่ต้องเรียนก่อนต้องเป็นตัวเลข")
    if course_id is not None and prereq == int(course_id):
        raise ValueError("วิชาที่ต้องเรียนก่อนเป็นคอร์สตัวเองไม่ได้")
    if not run_query("SELECT course_id FROM course WHERE course_id = %s", (prereq,)):
        raise ValueError(f"ไม่พบคอร์สรหัส {prereq} ที่จะใช้เป็นวิชาที่ต้องเรียนก่อน")
    return prereq


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
    """ดึง คอร์ส 1 รายการตาม course_id"""
    sql = "SELECT * FROM course WHERE course_id = %s"
    rows = run_query(sql, (course_id,))
    return rows[0] if rows else None


def create_course(data):
    """เพิ่ม คอร์ส ใหม่"""
    seat_limit = _clean_seat_limit(data.get("seat_limit"), default=50)
    prereq = _clean_prerequisite(data.get("prerequisite_id"))

    sql = "INSERT INTO course (title, category, price, seat_limit, prerequisite_id) VALUES (%s, %s, %s, %s, %s)"
    params = (data.get("title"), data.get("category"), data.get("price"), seat_limit, prereq)
    return run_command(sql, params)


def update_course(course_id, data):
    """แก้ไข คอร์ส"""
    existing = get_course(course_id)
    if not existing:
        raise ValueError(f"ไม่พบคอร์สรหัส {course_id} ในระบบ")

    seat_limit = _clean_seat_limit(data.get("seat_limit"), default=existing["seat_limit"])
    used = run_query(
        "SELECT COUNT(*) AS cnt FROM enrollment WHERE course_id = %s AND status <> 'dropped'",
        (course_id,))[0]["cnt"]
    if seat_limit is not None and seat_limit < used:
        raise ValueError(f"ตั้งที่นั่งเป็น {seat_limit} ไม่ได้ เพราะมีผู้ลงทะเบียนอยู่แล้ว {used} คน")

    prereq = _clean_prerequisite(data.get("prerequisite_id"), course_id=course_id)

    sql = "UPDATE course SET title = %s, category = %s, price = %s, seat_limit = %s, prerequisite_id = %s WHERE course_id = %s"
    params = (data.get("title"), data.get("category"), data.get("price"), seat_limit, prereq, course_id)
    return run_command(sql, params)


def delete_course(course_id):
    """ลบ คอร์ส ตาม course_id"""
    sql = "DELETE FROM course WHERE course_id = %s"
    return run_command(sql, (course_id,))


# ---------- การลงทะเบียน (enrollment) ----------
def search_enrollments(filters):
    """ค้นหา การลงทะเบียน ตามเงื่อนไข"""
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
    """ดึง การลงทะเบียน 1 รายการ — JOIN เพื่อดึง promo_code มาแสดงในฟอร์มแก้ไข"""
    sql = """
        SELECT e.*, p.promo_code
        FROM enrollment e
        LEFT JOIN promotion p ON e.promo_id = p.promo_id
        WHERE e.enroll_id = %s
    """
    rows = run_query(sql, (enroll_id,))
    return rows[0] if rows else None


def _validate_enrollment(learner_id, course_id, promo_code, exclude_enroll_id=None):
    """ด่านตรวจข้อมูลก่อนลงทะเบียน (เช็คผู้เรียน, คอร์ส, ที่นั่งเต็ม, ลงซ้ำ)"""
    if not learner_id or not course_id:
        raise ValueError("กรุณาระบุรหัสผู้เรียนและรหัสคอร์สให้ครบถ้วน")

    if not run_query("SELECT learner_id FROM learner WHERE learner_id = %s", (learner_id,)):
        raise ValueError(f"ไม่พบผู้เรียนรหัส {learner_id} ในระบบ")

    course_rows = run_query("SELECT price, seat_limit FROM course WHERE course_id = %s", (course_id,))
    if not course_rows:
        raise ValueError(f"ไม่พบคอร์สรหัส {course_id} ในระบบ")
    course = course_rows[0]

    exclude_sql = ""
    exclude_params = ()
    if exclude_enroll_id:
        exclude_sql = " AND enroll_id <> %s"
        exclude_params = (exclude_enroll_id,)

    # เช็คลงคอร์สซ้ำ
    dup = run_query(
        "SELECT COUNT(*) AS cnt FROM enrollment WHERE learner_id = %s AND course_id = %s AND status <> 'dropped'" + exclude_sql,
        (learner_id, course_id) + exclude_params)[0]["cnt"]
    if dup > 0:
        raise ValueError("ผู้เรียนคนนี้ลงทะเบียนคอร์สนี้ไปแล้ว")

    # เช็คที่นั่งเต็ม
    used = run_query(
        "SELECT COUNT(*) AS cnt FROM enrollment WHERE course_id = %s AND status <> 'dropped'" + exclude_sql,
        (course_id,) + exclude_params)[0]["cnt"]
    if course["seat_limit"] is not None and used >= course["seat_limit"]:
        raise ValueError(f"คอร์สนี้เต็มแล้ว (รับได้ {course['seat_limit']} ที่ - ลงทะเบียนแล้ว {used} ที่)")

    # เช็คโปรโมชัน
    promo_id = None
    discount_pct = 0
    if promo_code:
        promo_rows = run_query(
            "SELECT promo_id, discount_pct, (CURDATE() BETWEEN start_date AND end_date) AS is_valid FROM promotion WHERE promo_code = %s",
            (promo_code,))
        if not promo_rows:
            raise ValueError(f"ไม่พบโค้ดโปรโมชัน '{promo_code}' ในระบบ")
        if not promo_rows[0]["is_valid"]:
            raise ValueError(f"โค้ดโปรโมชัน '{promo_code}' หมดอายุหรือยังไม่เริ่มใช้งาน")
        promo_id = promo_rows[0]["promo_id"]
        discount_pct = float(promo_rows[0]["discount_pct"])

    return float(course["price"]), promo_id, discount_pct


def create_enrollment(data):
    """เพิ่ม การลงทะเบียน ใหม่"""
    learner_id = data.get("learner_id")
    course_id = data.get("course_id")
    status = data.get("status", "active")

    base_price, promo_id, discount_pct = _validate_enrollment(learner_id, course_id, data.get("promo_code"))
    paid_amount = round(base_price - (base_price * discount_pct / 100), 2)

    sql = """
        INSERT INTO enrollment (learner_id, course_id, status, paid_amount, promo_id)
        VALUES (%s, %s, %s, %s, %s)
    """
    return run_command(sql, (learner_id, course_id, status, paid_amount, promo_id))


def update_enrollment(enroll_id, data):
    """แก้ไข การลงทะเบียน"""
    learner_id = data.get("learner_id")
    course_id = data.get("course_id")
    status = data.get("status", "active")

    base_price, promo_id, discount_pct = _validate_enrollment(learner_id, course_id, data.get("promo_code"), exclude_enroll_id=enroll_id)
    paid_amount = round(base_price - (base_price * discount_pct / 100), 2)

    sql = """
        UPDATE enrollment 
        SET learner_id = %s, course_id = %s, status = %s, paid_amount = %s, promo_id = %s
        WHERE enroll_id = %s
    """
    return run_command(sql, (learner_id, course_id, status, paid_amount, promo_id, enroll_id))


def delete_enrollment(enroll_id):
    """ลบ การลงทะเบียน"""
    sql = "DELETE FROM enrollment WHERE enroll_id = %s"
    return run_command(sql, (enroll_id,))


# ============================================================
#  REPORT (รายงาน)
# ============================================================
def report_summary():
    """ตัวเลขสรุปบนการ์ด dashboard"""
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
    """✅ อัตราการเรียนจบต่อคอร์ส"""
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
def _format_promo_dates(rows):
    """แปลงวันที่เป็น YYYY-MM-DD เพื่อให้ช่องปฏิทินในฟอร์มแก้ไขแสดงผลได้ถูกต้อง"""
    for row in rows:
        for key in ("start_date", "end_date"):
            if isinstance(row.get(key), (datetime.date, datetime.datetime)):
                row[key] = row[key].strftime("%Y-%m-%d")
    return rows


def _validate_promotion(data, promo_id=None):
    """ตรวจสอบความถูกต้องของข้อมูลโปรโมชันก่อนบันทึก"""
    code = (data.get("promo_code") or "").strip().upper()
    if not code:
        raise ValueError("กรุณากรอกโค้ดส่วนลด")

    try:
        pct = float(data.get("discount_pct"))
    except (TypeError, ValueError):
        raise ValueError("เปอร์เซ็นต์ส่วนลดต้องเป็นตัวเลข")
    if pct <= 0 or pct > 100:
        raise ValueError("เปอร์เซ็นต์ส่วนลดต้องอยู่ระหว่าง 1–100")

    end_date = data.get("end_date")
    if not end_date:
        raise ValueError("กรุณาเลือกวันที่สิ้นสุด")
    if str(end_date) < datetime.date.today().strftime("%Y-%m-%d"):
        raise ValueError("วันที่สิ้นสุดต้องไม่ใช่วันที่ผ่านมาแล้ว")

    sql = "SELECT COUNT(*) AS cnt FROM promotion WHERE promo_code = %s"
    params = [code]
    if promo_id:
        sql += " AND promo_id <> %s"
        params.append(promo_id)
    if run_query(sql, params)[0]["cnt"] > 0:
        raise ValueError(f"โค้ด '{code}' มีอยู่ในระบบแล้ว")

    vip_only = 1 if str(data.get("vip_only", "0")) == "1" else 0
    return code, pct, end_date, vip_only


def get_all_promotions():
    return _format_promo_dates(run_query("SELECT * FROM promotion"))


def search_promotions(filters):
    sql = "SELECT * FROM promotion WHERE 1=1"
    params = []
    if filters.get("promo_code"):
        sql += " AND promo_code LIKE %s"
        params.append(f"%{filters['promo_code']}%")
    return _format_promo_dates(run_query(sql, params))


def get_promotion(promo_id):
    rows = _format_promo_dates(run_query("SELECT * FROM promotion WHERE promo_id = %s", (promo_id,)))
    return rows[0] if rows else None


def create_promotion(data):
    """สร้างโปรโมชัน — start_date ใช้ CURDATE() (วันที่สร้างโค้ดอัตโนมัติ)"""
    code, pct, end_date, vip_only = _validate_promotion(data)
    sql = """
        INSERT INTO promotion (promo_code, discount_pct, start_date, end_date, vip_only)
        VALUES (%s, %s, CURDATE(), %s, %s)
    """
    return run_command(sql, (code, pct, end_date, vip_only))


def update_promotion(promo_id, data):
    """แก้ไขโปรโมชัน — ไม่แตะ start_date เพื่อคงวันที่สร้างเดิมไว้"""
    if not get_promotion(promo_id):
        raise ValueError(f"ไม่พบโปรโมชันรหัส {promo_id}")
    code, pct, end_date, vip_only = _validate_promotion(data, promo_id=promo_id)
    sql = """
        UPDATE promotion
        SET promo_code = %s, discount_pct = %s, end_date = %s, vip_only = %s
        WHERE promo_id = %s
    """
    return run_command(sql, (code, pct, end_date, vip_only, promo_id))


def delete_promotion(promo_id):
    used = run_query("SELECT COUNT(*) AS cnt FROM enrollment WHERE promo_id = %s", (promo_id,))[0]["cnt"]
    if used > 0:
        raise ValueError(f"ลบไม่ได้ เพราะโค้ดนี้ถูกใช้ในการลงทะเบียนแล้ว {used} รายการ")
    return run_command("DELETE FROM promotion WHERE promo_id = %s", (promo_id,))


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
    """📊 รายงานการใช้งานโปรโมชันและยอดส่วนลด"""
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