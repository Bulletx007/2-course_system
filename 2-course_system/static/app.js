// ============================================================
//  app.js  —  ตรรกะหน้าเว็บ
//  หน้าที่: สร้างฟอร์มค้นหา/เพิ่ม/แก้ไขจาก ENTITIES แล้วส่ง request ไปที่ app.py
// ============================================================

// [แก้ไข]: เรียงลำดับใหม่ให้ "learners" อยู่บนสุด
// หน้าที่: Object.keys(ENTITIES)[0] จะได้ "learners" ทำให้เปิดเว็บมาเจอแท็บผู้เรียนเป็นแท็บแรกเอง
const ENTITIES = {
  "learners": {
    "label": "ผู้เรียน",
    "api": "/api/learners",
    "idKey": "learner_id",
    "search": [
      { "key": "name", "label": "ชื่อ", "type": "text" },
      { "key": "email", "label": "อีเมล", "type": "text" }
    ],
    "form": [
      { "key": "name", "label": "ชื่อ", "type": "text" },
      { "key": "email", "label": "อีเมล", "type": "text" },
      // ไม่มีช่อง join_date เพราะ db.py ใส่วันที่สมัคร (CURDATE) ให้เอง และคงค่าเดิมไว้ตอนแก้ไข
      { "key": "member_tier", "label": "ระดับสมาชิก", "type": "select", "options": ["normal", "vip"] }
    ]
  },

  "courses": {
    "label": "คอร์ส",
    "api": "/api/courses",
    "idKey": "course_id",
    "search": [
      { "key": "title", "label": "ชื่อคอร์ส", "type": "text" },
      {
        "key": "category", "label": "หมวดหมู่", "type": "select",
        "options": ["", "Programming", "Database", "Design", "Business"]
      }
    ],
    "form": [
      { "key": "title", "label": "ชื่อคอร์ส", "type": "text" },
      {
        "key": "category", "label": "หมวดหมู่", "type": "select",
        "options": ["Programming", "Database", "Design", "Business"]
      },
      { "key": "price", "label": "ราคา", "type": "number" },
      // [เพิ่มใหม่]: ช่องจำนวนที่นั่ง ชื่อ key ต้องตรงกับคอลัมน์ seat_limit ในฐานข้อมูล
      { "key": "seat_limit", "label": "จำนวนที่นั่ง (ถ้าเว้นว่างจะใช้ 50)", "type": "number" },
      { "key": "prerequisite_id", "label": "รหัสวิชาที่ต้องเรียนก่อน (ถ้ามี)", "type": "number" }
    ]
  },

  "enrollments": {
    "label": "การลงทะเบียน",
    "api": "/api/enrollments",
    "idKey": "enroll_id",
    "search": [
      { "key": "learner_id", "label": "รหัสผู้เรียน", "type": "number" },
      { "key": "course_id", "label": "รหัสคอร์ส", "type": "number" },
      { "key": "status", "label": "สถานะ", "type": "select", "options": ["", "active", "completed", "dropped"] }
    ],
    "form": [
      { "key": "learner_id", "label": "รหัสผู้เรียน", "type": "number" },
      { "key": "course_id", "label": "รหัสคอร์ส", "type": "number" },
      // [เพิ่มใหม่]: พิมพ์โค้ดส่วนลดเป็นตัวหนังสือได้เลย หลังบ้านจะแปลงเป็น promo_id และคำนวณราคาให้
      { "key": "promo_code", "label": "โค้ดโปรโมชัน (ถ้ามี เช่น VIP50)", "type": "text" },
      { "key": "status", "label": "สถานะ", "type": "select", "options": ["active", "completed", "dropped"] }
    ]
  },

  "lessons": {
    "label": "บทเรียน",
    "api": "/api/lessons",
    "idKey": "lesson_id",
    "search": [
      { "key": "title", "label": "ชื่อบทเรียน", "type": "text" }
    ],
    "form": [
      { "key": "course_id", "label": "รหัสคอร์ส", "type": "number" },
      { "key": "title", "label": "ชื่อบทเรียน", "type": "text" },
      { "key": "seq_no", "label": "ลำดับบทเรียน", "type": "number" },
      { "key": "duration_min", "label": "ระยะเวลา (นาที)", "type": "number" }
    ]
  },

  "promotions": {
    "label": "โปรโมชัน",
    "api": "/api/promotions",
    "idKey": "promo_id",
    "search": [
      { "key": "promo_code", "label": "โค้ดส่วนลด", "type": "text" }
    ],
    "form": [
      { "key": "promo_code", "label": "โค้ดส่วนลด", "type": "text" },
      { "key": "discount_pct", "label": "เปอร์เซ็นต์ส่วนลด (%)", "type": "number" },
      // [ลบออก]: ช่อง start_date (วันที่เริ่ม)
      // เหตุผล: db.create_promotion ใส่ CURDATE() หรือวันที่สร้างโค้ดให้อัตโนมัติ ผู้ใช้ไม่ต้องกรอก
      { "key": "end_date", "label": "วันที่สิ้นสุด", "type": "date" },
      // [เพิ่มใหม่]: เลือกว่าโค้ดนี้ใช้ได้เฉพาะสมาชิก VIP หรือไม่ (ตารางมีคอลัมน์ vip_only อยู่แล้ว)
      { "key": "vip_only", "label": "เฉพาะ VIP (0 = ทุกคนใช้ได้, 1 = เฉพาะ VIP)", "type": "select", "options": ["0", "1"] }
    ]
  }
};

let current = Object.keys(ENTITIES)[0];   // = "learners" เพราะอยู่บนสุดแล้ว
let editingId = null;
const $ = (s) => document.querySelector(s);
function setStatus(el, msg, cls = "") { el.className = "status " + cls; el.textContent = msg; }
async function api(url, opts) { const res = await fetch(url, opts); return res.json(); }

function fieldHtml(f, prefix, value = "") {
  let input;
  if (f.type === "select") {
    // [แก้ไข]: เดิมเทียบ o === value ตรงๆ
    // ปัญหา: ฐานข้อมูลส่ง vip_only มาเป็นตัวเลข 1 แต่ option เป็นข้อความ "1" → เทียบไม่ตรง ฟอร์มเลยเลือก "0" ผิด
    // หน้าที่: แปลงทั้งสองฝั่งเป็นข้อความก่อนเทียบ ตอนกดแก้ไขจะเลือกค่าเดิมได้ถูกต้อง
    input = '<select id="' + prefix + f.key + '">' +
      f.options.map(o => '<option value="' + o + '"' +
        (String(o) === String(value ?? "") ? " selected" : "") + '>' +
        (o || "ทั้งหมด / ไม่มี") + '</option>').join("") + '</select>';
  } else {
    input = '<input id="' + prefix + f.key + '" type="' + f.type + '" value="' + (value ?? "") + '">';
  }
  return '<div class="field"><label>' + f.label + '</label>' + input + '</div>';
}

function buildSearch() {
  const cfg = ENTITIES[current];
  $("#searchTitle").textContent = cfg.label;
  $("#searchFields").innerHTML = cfg.search.map(f => fieldHtml(f, "s_")).join("");
}

async function doSearch() {
  const cfg = ENTITIES[current];
  const params = new URLSearchParams();
  cfg.search.forEach(f => { const v = $("#s_" + f.key).value; if (v) params.append(f.key, v); });
  setStatus($("#status"), "กำลังค้นหา...");
  renderTable(await api(cfg.api + "?" + params.toString()));
}

function renderTable(r) {
  const head = $("#tableHead"), body = $("#tableBody"), st = $("#status");
  head.innerHTML = ""; body.innerHTML = "";
  if (!r.ok) { setStatus(st, (r.todo ? "🚧 " : "⚠️ ") + r.error, r.todo ? "todo" : "err"); return; }
  const rows = r.data || [];
  if (rows.length === 0) { setStatus(st, "ไม่พบข้อมูล"); return; }
  setStatus(st, "พบ " + rows.length + " รายการ");
  const cols = Object.keys(rows[0]);
  head.innerHTML = cols.map(c => "<th>" + c + "</th>").join("") + "<th>จัดการ</th>";
  body.innerHTML = rows.map(row => {
    const id = row[ENTITIES[current].idKey];
    return "<tr>" + cols.map(c => "<td>" + (row[c] ?? "—") + "</td>").join("") +
      '<td><button class="btn sm" onclick="editRow(' + id + ')">แก้ไข</button> ' +
      '<button class="btn sm del" onclick="deleteRow(' + id + ')">ลบ</button></td></tr>';
  }).join("");
}

function openForm(title, data = {}) {
  const cfg = ENTITIES[current];
  $("#modalTitle").textContent = title;
  // เติมค่าเดิมลงฟอร์มตามชื่อ key (ชื่อ key ต้องตรงกับชื่อคอลัมน์ที่ API ส่งมา)
  $("#formFields").innerHTML = cfg.form.map(f => fieldHtml(f, "f_", data[f.key])).join("");
  $("#modal").classList.remove("hidden");
}

function collectForm() {
  const cfg = ENTITIES[current], d = {};
  cfg.form.forEach(f => d[f.key] = $("#f_" + f.key).value);
  return d;
}

async function editRow(id) {
  const cfg = ENTITIES[current];
  const r = await api(cfg.api + "/" + id);
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  editingId = id; openForm("แก้ไขข้อมูล", r.data);
}

async function deleteRow(id) {
  if (!confirm("ยืนยันการลบ?")) return;
  const r = await api(ENTITIES[current].api + "/" + id, { method: "DELETE" });
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  doSearch();
}

async function save() {
  const cfg = ENTITIES[current], data = collectForm();
  const opts = {
    method: editingId ? "PUT" : "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  };
  const r = await api(editingId ? cfg.api + "/" + editingId : cfg.api, opts);
  // ถ้า db.py raise ValueError (เช่น คอร์สเต็ม หรือโค้ดซ้ำ) ข้อความภาษาไทยจะขึ้นเป็น alert ตรงนี้
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  $("#modal").classList.add("hidden"); doSearch();
}

document.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
  t.classList.add("active"); current = t.dataset.entity;
  buildSearch(); $("#tableHead").innerHTML = ""; $("#tableBody").innerHTML = "";
  setStatus($("#status"), 'กด "ค้นหา" เพื่อแสดงข้อมูล');
}));
$("#btnSearch").onclick = doSearch;
$("#btnClear").onclick = () => buildSearch();
$("#btnAdd").onclick = () => { editingId = null; openForm("เพิ่มข้อมูลใหม่"); };
$("#btnSave").onclick = save;
$("#btnCancel").onclick = () => $("#modal").classList.add("hidden");

// ---------- เริ่มต้นตอนเปิดหน้าเว็บ ----------
// ไฮไลต์ปุ่มแท็บให้ตรงกับ current (ผู้เรียน)
document.querySelectorAll(".tab").forEach(t => {
  t.classList.toggle("active", t.dataset.entity === current);
});

// [แก้ไข]: เดิมเรียก buildSearch() และ setStatus() ซ้ำ 2 รอบ เหลือรอบเดียวพอ
buildSearch();
setStatus($("#status"), 'กด "ค้นหา" เพื่อแสดงข้อมูล');