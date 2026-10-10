# ============================================================
#  app.py — เว็บแอป Flask
# ============================================================
from flask import Flask, request, jsonify, render_template
import db

app = Flask(__name__)


def safe(fn, *args, **kwargs):
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


# ============================================================
#  ★ [ส่วนที่เพิ่มเข้ามาใหม่] API สำหรับ โปรโมชัน (Promotions)
# ============================================================
@app.route("/api/promotions", methods=["GET"])
def api_promotions():
    # รองรับการค้นหาโปรโมชันตามรหัส (promo_code)
    promo_code = request.args.get("promo_code")
    if promo_code:
        sql = "SELECT * FROM promotion WHERE promo_code LIKE %s"
        return jsonify({"ok": True, "data": db.run_query(sql, (f"%{promo_code}%",))})
    return jsonify({"ok": True, "data": db.get_all_promotions()})

@app.route("/api/promotions/<int:promo_id>", methods=["GET"])
def api_get_promotion(promo_id):
    # ดึงข้อมูลโปรโมชันตาม ID สำหรับปุ่มแก้ไข
    sql = "SELECT * FROM promotion WHERE promo_id = %s"
    rows = db.run_query(sql, (promo_id,))
    if rows:
        return jsonify({"ok": True, "data": rows[0]})
    return jsonify({"ok": False, "error": "ไม่พบข้อมูลโปรโมชัน"})

@app.route("/api/promotions", methods=["POST"])
def api_create_promotion():
    # เพิ่มโปรโมชันใหม่เข้าฐานข้อมูล
    data = request.get_json()
    sql = "INSERT INTO promotion (promo_code, discount_pct, start_date, end_date, vip_only) VALUES (%s, %s, %s, %s, %s)"
    params = (data.get("promo_code"), data.get("discount_pct"), data.get("start_date"), data.get("end_date"), 0)
    db.run_command(sql, params)
    return jsonify({"ok": True})

@app.route("/api/promotions/<int:promo_id>", methods=["PUT"])
def api_update_promotion(promo_id):
    # แก้ไขข้อมูลโปรโมชันตาม ID
    data = request.get_json()
    sql = "UPDATE promotion SET promo_code = %s, discount_pct = %s, start_date = %s, end_date = %s WHERE promo_id = %s"
    params = (data.get("promo_code"), data.get("discount_pct"), data.get("start_date"), data.get("end_date"), promo_id)
    db.run_command(sql, params)
    return jsonify({"ok": True})

@app.route("/api/promotions/<int:promo_id>", methods=["DELETE"])
def api_delete_promotion(promo_id):
    # ลบข้อมูลโปรโมชันตาม ID
    sql = "DELETE FROM promotion WHERE promo_id = %s"
    db.run_command(sql, (promo_id,))
    return jsonify({"ok": True})


# ============================================================
#  ★ [ส่วนที่เพิ่มเข้ามาใหม่] API สำหรับ บทเรียน (Lessons)
# ============================================================
@app.route("/api/lessons", methods=["GET"])
def api_lessons():
    # รองรับการค้นหาบทเรียนตามชื่อ (title) พร้อม Join ดึงชื่อคอร์ส
    title = request.args.get("title")
    if title:
        sql = """
            SELECT l.lesson_id, c.title AS course_title, l.title AS lesson_title, l.seq_no, l.duration_min
            FROM lesson l
            INNER JOIN course c ON l.course_id = c.course_id
            WHERE l.title LIKE %s
            ORDER BY c.course_id, l.seq_no
        """
        return jsonify({"ok": True, "data": db.run_query(sql, (f"%{title}%",))})
    return jsonify({"ok": True, "data": db.get_all_lessons_with_course()})

@app.route("/api/lessons/<int:lesson_id>", methods=["GET"])
def api_get_lesson(lesson_id):
    # ดึงข้อมูลบทเรียนตาม ID สำหรับปุ่มแก้ไข
    sql = "SELECT * FROM lesson WHERE lesson_id = %s"
    rows = db.run_query(sql, (lesson_id,))
    if rows:
        return jsonify({"ok": True, "data": rows[0]})
    return jsonify({"ok": False, "error": "ไม่พบข้อมูลบทเรียน"})

@app.route("/api/lessons", methods=["POST"])
def api_create_lesson():
    # เพิ่มบทเรียนใหม่เข้าฐานข้อมูล
    data = request.get_json()
    sql = "INSERT INTO lesson (course_id, title, seq_no, duration_min) VALUES (%s, %s, %s, %s)"
    params = (data.get("course_id"), data.get("title"), data.get("seq_no"), data.get("duration_min"))
    db.run_command(sql, params)
    return jsonify({"ok": True})

@app.route("/api/lessons/<int:lesson_id>", methods=["PUT"])
def api_update_lesson(lesson_id):
    # แก้ไขข้อมูลบทเรียนตาม ID
    data = request.get_json()
    sql = "UPDATE lesson SET course_id = %s, title = %s, seq_no = %s, duration_min = %s WHERE lesson_id = %s"
    params = (data.get("course_id"), data.get("title"), data.get("seq_no"), data.get("duration_min"), lesson_id)
    db.run_command(sql, params)
    return jsonify({"ok": True})

@app.route("/api/lessons/<int:lesson_id>", methods=["DELETE"])
def api_delete_lesson(lesson_id):
    # ลบข้อมูลบทเรียนตาม ID
    sql = "DELETE FROM lesson WHERE lesson_id = %s"
    db.run_command(sql, (lesson_id,))
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)