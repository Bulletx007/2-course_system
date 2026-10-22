# ============================================================
#  app.py — เว็บแอป Flask
#  หน้าที่: รับ request จากหน้าเว็บ (app.js) แล้วเรียกฟังก์ชันใน db.py
#           ส่งผลกลับเป็น JSON รูปแบบ {"ok": True/False, "data": ..., "error": ...}
# ============================================================
from flask import Flask, request, jsonify, render_template
import db

app = Flask(__name__)


def safe(fn, *args, **kwargs):
    """ตัวครอบทุก API: ถ้าสำเร็จคืน {"ok": True, "data": ...}
    ถ้าเกิด Error (รวม ValueError ภาษาไทยที่เรา raise ใน db.py) จะคืน {"ok": False, "error": ...}
    ให้หน้าเว็บแสดงเป็น alert ได้ แทนที่จะพังเป็นหน้า HTML 500"""
    try:
        return jsonify({"ok": True, "data": fn(*args, **kwargs)})
    except NotImplementedError as e:
        return jsonify({"ok": False, "todo": True, "error": str(e)}), 501
    except Exception as e:
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 500


@app.route("/")
def page_home():
    return render_template("index.html")

@app.route("/report")
def page_report():
    return render_template("report.html")


# ---- ผู้เรียน ----
@app.route("/api/learners", methods=["GET"])
def learners_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_learners, filters)

@app.route("/api/learners/<int:_id>", methods=["GET"])
def learner_get(_id):
    return safe(db.get_learner, _id)

@app.route("/api/learners", methods=["POST"])
def learner_create():
    return safe(db.create_learner, request.json)

@app.route("/api/learners/<int:_id>", methods=["PUT"])
def learner_update(_id):
    return safe(db.update_learner, _id, request.json)

@app.route("/api/learners/<int:_id>", methods=["DELETE"])
def learner_delete(_id):
    return safe(db.delete_learner, _id)


# ---- คอร์ส ----
@app.route("/api/courses", methods=["GET"])
def courses_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_courses, filters)

@app.route("/api/courses/<int:_id>", methods=["GET"])
def course_get(_id):
    return safe(db.get_course, _id)

@app.route("/api/courses", methods=["POST"])
def course_create():
    return safe(db.create_course, request.json)

@app.route("/api/courses/<int:_id>", methods=["PUT"])
def course_update(_id):
    return safe(db.update_course, _id, request.json)

@app.route("/api/courses/<int:_id>", methods=["DELETE"])
def course_delete(_id):
    return safe(db.delete_course, _id)


# ---- การลงทะเบียน ----
@app.route("/api/enrollments", methods=["GET"])
def enrollments_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_enrollments, filters)

@app.route("/api/enrollments/<int:_id>", methods=["GET"])
def enrollment_get(_id):
    return safe(db.get_enrollment, _id)

@app.route("/api/enrollments", methods=["POST"])
def enrollment_create():
    return safe(db.create_enrollment, request.json)

@app.route("/api/enrollments/<int:_id>", methods=["PUT"])
def enrollment_update(_id):
    return safe(db.update_enrollment, _id, request.json)

@app.route("/api/enrollments/<int:_id>", methods=["DELETE"])
def enrollment_delete(_id):
    return safe(db.delete_enrollment, _id)


# ---- รายงาน ----
@app.route("/api/reports/summary")
def report_summary():
    return safe(db.report_summary)

@app.route("/api/reports/popular-courses")
def route_report_popular_courses():
    return safe(db.report_popular_courses)

@app.route("/api/reports/completion-rate")
def route_report_completion_rate():
    return safe(db.report_completion_rate)

@app.route("/api/reports/prerequisites")
def route_report_course_prerequisites():
    return safe(db.report_course_prerequisites)

@app.route("/api/reports/promotions")
def route_report_promotions():
    """ดึงรายงานการใช้งานโปรโมชัน (เรียก db.report_promotion_usage)"""
    return safe(db.report_promotion_usage)


# ============================================================
#  ★ API สำหรับ โปรโมชัน (Promotions)
#  [แก้ไขทั้งหมด]: ลบ SQL ที่เขียนเองใน app.py ออก แล้วเรียกฟังก์ชันใน db.py แทน
#  หน้าที่: ให้ start_date ใส่ CURDATE() อัตโนมัติ, แปลงวันที่เป็น YYYY-MM-DD,
#           เช็คโค้ดซ้ำ/ส่วนลด/วันหมดอายุ และแสดง Error ภาษาไทยผ่าน safe()
# ============================================================
@app.route("/api/promotions", methods=["GET"])
def api_promotions():
    # [แก้ไข]: เดิมเขียน SQL LIKE เองที่นี่ → ใช้ db.search_promotions (ไม่มีเงื่อนไข = ได้ทั้งหมด)
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_promotions, filters)

@app.route("/api/promotions/<int:promo_id>", methods=["GET"])
def api_get_promotion(promo_id):
    # [แก้ไข]: ใช้ db.get_promotion ซึ่งแปลงวันที่เป็น YYYY-MM-DD ช่องปฏิทินในฟอร์มแก้ไขจึงแสดงวันที่เดิมได้
    return safe(db.get_promotion, promo_id)

@app.route("/api/promotions", methods=["POST"])
def api_create_promotion():
    # [แก้ไข]: เดิม INSERT start_date จากฟอร์ม (ซึ่งตอนนี้ไม่มีแล้ว จึงเป็นค่าว่าง)
    # → ใช้ db.create_promotion ที่ใส่ CURDATE() เป็นวันที่เริ่มให้อัตโนมัติ
    return safe(db.create_promotion, request.get_json())

@app.route("/api/promotions/<int:promo_id>", methods=["PUT"])
def api_update_promotion(promo_id):
    # [แก้ไข]: เดิม UPDATE start_date ทุกครั้ง ทำให้วันที่สร้างเดิมหาย
    # → ใช้ db.update_promotion ที่ไม่แตะ start_date
    return safe(db.update_promotion, promo_id, request.get_json())

@app.route("/api/promotions/<int:promo_id>", methods=["DELETE"])
def api_delete_promotion(promo_id):
    # [แก้ไข]: ใช้ db.delete_promotion ที่เช็คก่อนว่าโค้ดถูกใช้ลงทะเบียนไปแล้วหรือยัง
    return safe(db.delete_promotion, promo_id)


# ============================================================
#  ★ API สำหรับ บทเรียน (Lessons)
#  [แก้ไข]: SQL เหมือนเดิม แต่ครอบด้วย safe() ทุก route
#  หน้าที่: ถ้าเกิด Error (เช่นใส่รหัสคอร์สที่ไม่มีจริง → 1452) หน้าเว็บจะ alert ข้อความได้ ไม่พังเงียบ
# ============================================================
def _search_lessons(title):
    """ค้นหาบทเรียนตามชื่อ ถ้าไม่กรอกชื่อจะได้ทั้งหมดพร้อมชื่อคอร์ส"""
    if title:
        sql = """
            SELECT l.lesson_id, c.title AS course_title, l.title AS lesson_title, l.seq_no, l.duration_min
            FROM lesson l
            INNER JOIN course c ON l.course_id = c.course_id
            WHERE l.title LIKE %s
            ORDER BY c.course_id, l.seq_no
        """
        return db.run_query(sql, (f"%{title}%",))
    return db.get_all_lessons_with_course()

def _get_lesson(lesson_id):
    """ดึงบทเรียน 1 รายการ (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    rows = db.run_query("SELECT * FROM lesson WHERE lesson_id = %s", (lesson_id,))
    if not rows:
        raise ValueError("ไม่พบข้อมูลบทเรียน")
    return rows[0]

@app.route("/api/lessons", methods=["GET"])
def api_lessons():
    return safe(_search_lessons, request.args.get("title"))

@app.route("/api/lessons/<int:lesson_id>", methods=["GET"])
def api_get_lesson(lesson_id):
    return safe(_get_lesson, lesson_id)

@app.route("/api/lessons", methods=["POST"])
def api_create_lesson():
    data = request.get_json()
    sql = "INSERT INTO lesson (course_id, title, seq_no, duration_min) VALUES (%s, %s, %s, %s)"
    params = (data.get("course_id"), data.get("title"), data.get("seq_no"), data.get("duration_min"))
    return safe(db.run_command, sql, params)

@app.route("/api/lessons/<int:lesson_id>", methods=["PUT"])
def api_update_lesson(lesson_id):
    data = request.get_json()
    sql = "UPDATE lesson SET course_id = %s, title = %s, seq_no = %s, duration_min = %s WHERE lesson_id = %s"
    params = (data.get("course_id"), data.get("title"), data.get("seq_no"), data.get("duration_min"), lesson_id)
    return safe(db.run_command, sql, params)

@app.route("/api/lessons/<int:lesson_id>", methods=["DELETE"])
def api_delete_lesson(lesson_id):
    return safe(db.run_command, "DELETE FROM lesson WHERE lesson_id = %s", (lesson_id,))


if __name__ == "__main__":
    app.run(debug=True, port=5000)