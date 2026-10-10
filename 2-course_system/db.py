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
    # TODO: เขียน SQL ค้นหาแบบยืดหยุ่นตาม filters (ใช้ %s เสมอ)
    _todo("search_learners")

    # แก้
def search_learners(filters):
    sql = "SELECT * FROM learner WHERE 1=1"
    params = []
    if filters.get("name"):
        sql += " AND name LIKE %s"
        params.append(f"%{filters['name']}%")
    if filters.get("email"):
        sql += " AND email LIKE %s"              # เปลี่ยนจาก = เป็น LIKE
        params.append(f"%{filters['email']}%")   # เติม % ครอบหัวท้าย
    return run_query(sql, params)

def get_learner(learner_id):
    """ดึง ผู้เรียน 1 รายการตาม learner_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    # TODO: SELECT * FROM learner WHERE learner_id = %s แล้วคืนแถวเดียว
    _todo("get_learner")

    # แก้
def get_learner(learner_id):
    sql = "SELECT * FROM learner WHERE learner_id = %s"
    rows = run_query(sql, (learner_id,))
    return rows[0] if rows else None


def create_learner(data):
    """เพิ่ม ผู้เรียน ใหม่ — data มีคีย์: name, email, join_date"""
    # TODO: INSERT INTO learner (...) VALUES (%s, ...)
    _todo("create_learner")

    # แก้
def create_learner(data):
    sql = "INSERT INTO learner (name, email, join_date, member_tier) VALUES (%s, %s, %s, %s)"
    params = (data.get("name"), data.get("email"), data.get("join_date"), data.get("member_tier", "normal"))
    return run_command(sql, params)


def update_learner(learner_id, data):
    """แก้ไข ผู้เรียน ตาม learner_id"""
    # TODO: UPDATE learner SET ... WHERE learner_id=%s
    _todo("update_learner")

    # แก้
def update_learner(learner_id, data):
    sql = "UPDATE learner SET name = %s, email = %s, join_date = %s, member_tier = %s WHERE learner_id = %s"
    params = (data.get("name"), data.get("email"), data.get("join_date"), data.get("member_tier", "normal"), learner_id)
    return run_command(sql, params)

def delete_learner(learner_id):
    """ลบ ผู้เรียน ตาม learner_id"""
    # TODO: DELETE FROM learner WHERE learner_id=%s
    _todo("delete_learner")

    # แก้
def delete_learner(learner_id):
    sql = "DELETE FROM learner WHERE learner_id = %s"
    return run_command(sql, (learner_id,))


# ---------- คอร์ส (course) ----------
def search_courses(filters):
    """ค้นหา คอร์ส ตามเงื่อนไข (title, category)
    คำใบ้: เริ่มจาก sql = "SELECT * FROM course WHERE 1=1"
    แล้วต่อเงื่อนไขเฉพาะ filter ที่มีค่า (ข้อความใช้ LIKE %s, อื่น ๆ ใช้ = %s)"""
    # TODO: เขียน SQL ค้นหาแบบยืดหยุ่นตาม filters (ใช้ %s เสมอ)
    _todo("search_courses")
  # แก้
def search_courses(filters):
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
    # TODO: SELECT * FROM course WHERE course_id = %s แล้วคืนแถวเดียว
    _todo("get_course")

    # แก้
def get_course(course_id):
    sql = "SELECT * FROM course WHERE course_id = %s"
    rows = run_query(sql, (course_id,))
    return rows[0] if rows else None


def create_course(data):
    """เพิ่ม คอร์ส ใหม่ — data มีคีย์: title, category, price, prerequisite_id"""
    # TODO: INSERT INTO course (...) VALUES (%s, ...)
    _todo("create_course")

    # แก้
def create_course(data):
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
    # TODO: UPDATE course SET ... WHERE course_id=%s
    _todo("update_course")

    # แก้
def update_course(course_id, data):
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
    # TODO: DELETE FROM course WHERE course_id=%s
    _todo("delete_course")

    # แก้
def delete_course(course_id):
    sql = "DELETE FROM course WHERE course_id = %s"
    return run_command(sql, (course_id,))

# ---------- การลงทะเบียน (enrollment) ----------
def search_enrollments(filters):
    """ค้นหา การลงทะเบียน ตามเงื่อนไข (learner_id, course_id, status)
    คำใบ้: เริ่มจาก sql = "SELECT * FROM enrollment WHERE 1=1"
    แล้วต่อเงื่อนไขเฉพาะ filter ที่มีค่า (ข้อความใช้ LIKE %s, อื่น ๆ ใช้ = %s)"""
    # TODO: เขียน SQL ค้นหาแบบยืดหยุ่นตาม filters (ใช้ %s เสมอ)
    _todo("search_enrollments")

    # แก้
def search_enrollments(filters):
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
    # TODO: SELECT * FROM enrollment WHERE enroll_id = %s แล้วคืนแถวเดียว
    _todo("get_enrollment")
    # แก้
def get_enrollment(enroll_id):
    sql = "SELECT * FROM enrollment WHERE enroll_id = %s"
    rows = run_query(sql, (enroll_id,))
    return rows[0] if rows else None


def create_enrollment(data):
    """เพิ่ม การลงทะเบียน ใหม่ — data มีคีย์: learner_id, course_id, enroll_date, status"""
    # TODO: INSERT INTO enrollment (...) VALUES (%s, ...)
    _todo("create_enrollment")

    # แก้
def create_enrollment(data):
    sql = "INSERT INTO enrollment (learner_id, course_id, enroll_date, status, paid_amount, promo_id) VALUES (%s, %s, %s, %s, %s, %s)"
    params = (
        data.get("learner_id"),
        data.get("course_id"),
        data.get("enroll_date"),
        data.get("status", "active"),
        data.get("paid_amount", 0),
        data.get("promo_id") or None
    )
    return run_command(sql, params)

def update_enrollment(enroll_id, data):
    """แก้ไข การลงทะเบียน ตาม enroll_id"""
    # TODO: UPDATE enrollment SET ... WHERE enroll_id=%s
    _todo("update_enrollment")

    # แก้
def update_enrollment(enroll_id, data):
    sql = "UPDATE enrollment SET status = %s, paid_amount = %s WHERE enroll_id = %s"
    params = (
        data.get("status"),
        data.get("paid_amount"),
        enroll_id
    )
    return run_command(sql, params)

def delete_enrollment(enroll_id):
    """ลบ การลงทะเบียน ตาม enroll_id"""
    # TODO: DELETE FROM enrollment WHERE enroll_id=%s
    _todo("delete_enrollment")

    # แก้
def delete_enrollment(enroll_id):
    sql = "DELETE FROM enrollment WHERE enroll_id = %s"
    return run_command(sql, (enroll_id,))


# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
# ============================================================
def report_summary():
    """ตัวเลขสรุปบนการ์ด dashboard — คืน dict เช่น {"learners": 10, ...}
    คำใบ้: ใช้ COUNT(*) หลายครั้ง"""
    # TODO: นับจำนวนรวมต่าง ๆ เพื่อแสดงบนการ์ด
    _todo("report_summary")

    # แก้
def report_summary():
    # นับจำนวนข้อมูลรวมทั้งหมดในแต่ละตาราง เพื่อนำไปแสดงเป็นการ์ดสรุปผลบนหน้า Dashboard
    learners = run_query("SELECT COUNT(*) AS cnt FROM learner")[0]["cnt"]
    courses = run_query("SELECT COUNT(*) AS cnt FROM course")[0]["cnt"]
    enrollments = run_query("SELECT COUNT(*) AS cnt FROM enrollment")[0]["cnt"]
    completed = run_query("SELECT COUNT(*) AS cnt FROM enrollment WHERE status='completed'")[0]["cnt"]
    return {
        "learners": learners,
        "courses": courses,
        "enrollments": enrollments,
        "completed": completed
    }
    

def report_popular_courses():
    """📈 คอร์สยอดนิยม (Most Enrolled)
    คำใบ้: JOIN enrollment→course, GROUP BY course, COUNT, ORDER BY DESC, LIMIT 5"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_popular_courses")

    # แก้
def report_popular_courses():
    # ใช้ INNER JOIN เชื่อมตารางคอร์สกับประวัติการลงทะเบียนเพื่อนับจำนวนนักเรียน
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
    """✅ อัตราการเรียนจบต่อคอร์ส (Completion Rate)
    คำใบ้: GROUP BY course, นับ completed เทียบทั้งหมด ด้วย SUM(CASE WHEN ...)"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_completion_rate")

    # แก้
def report_completion_rate():
    # ใช้ SUM(CASE WHEN ...) เพื่อแยกนับเฉพาะคนที่เรียนจบ แล้วคำนวณเทียบกับจำนวนทั้งหมดเป็นเปอร์เซ็นต์
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
    """🔗 คอร์สและวิชาที่ต้องเรียนก่อน (Self-Join)
    คำใบ้: self-join: course c LEFT JOIN course pre ON c.prerequisite_id = pre.course_id"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_course_prerequisites")

    # แก้
def report_course_prerequisites():
    # ใช้ Self-Join เชื่อมตารางคอร์สเข้าหากับตัวเองผ่าน prerequisite_id เพื่อดึงชื่อวิชาบังคับก่อนออกมาแสดง
    sql = """
        SELECT c.course_id, c.title AS course_title, c.category,
               pre.course_id AS prerequisite_id, pre.title AS prerequisite_title
        FROM course c
        LEFT JOIN course pre ON c.prerequisite_id = pre.course_id
    """
    return run_query(sql)



#---------------------------------------------------------------------------------------------------------------


#เพิ่มฟังก์ชัน get_all_promotions() เพื่อดึงข้อมูลโปรโมชันทั้งหมด
# ---------- โปรโมชัน (promotion) ----------
def get_all_promotions():
    return run_query("SELECT * FROM promotion")

#เพิ่มฟังก์ชัน get_all_lessons_with_course() เพื่อดึงข้อมูลบทเรียนพร้อมชื่อคอร์ส
# ---------- บทเรียน (lesson) ----------

def get_all_lessons_with_course():
    sql = """
        SELECT l.lesson_id, c.title AS course_title, l.title AS lesson_title, l.seq_no, l.duration_min
        FROM lesson l
        INNER JOIN course c ON l.course_id = c.course_id
        ORDER BY c.course_id, l.seq_no
    """
    return run_query(sql)