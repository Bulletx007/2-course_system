// ============================================================
//  app.js  —  ตรรกะหน้าเว็บ (อัปเดตฟอร์มการลงทะเบียนให้รองรับโค้ดโปรโมชันเป็นตัวหนังสือ)
// ============================================================
const ENTITIES = {
  "lessons": {
    "label": "บทเรียน",
    "api": "/api/lessons",
    "idKey": "lesson_id",
    "search": [
      {
        "key": "title",
        "label": "ชื่อบทเรียน",
        "type": "text"
      }
    ],
    "form": [
      {
        "key": "course_id",
        "label": "รหัสคอร์ส",
        "type": "number"
      },
      {
        "key": "title",
        "label": "ชื่อบทเรียน",
        "type": "text"
      },
      {
        "key": "seq_no",
        "label": "ลำดับบทเรียน",
        "type": "number"
      },
      {
        "key": "duration_min",
        "label": "ระยะเวลา (นาที)",
        "type": "number"
      }
    ]
  },
  "promotions": {
    "label": "โปรโมชัน",
    "api": "/api/promotions",
    "idKey": "promo_id",
    "search": [
      {
        "key": "promo_code",
        "label": "โค้ดส่วนลด",
        "type": "text"
      }
    ],
    "form": [
      {
        "key": "promo_code",
        "label": "โค้ดส่วนลด",
        "type": "text"
      },
      {
        "key": "discount_pct",
        "label": "เปอร์เซ็นต์ส่วนลด (%)",
        "type": "number"
      },
      {
        "key": "start_date",
        "label": "วันที่เริ่ม",
        "type": "date"
      },
      {
        "key": "end_date",
        "label": "วันที่สิ้นสุด",
        "type": "date"
      }
    ]
  },
  "learners": {
    "label": "ผู้เรียน",
    "api": "/api/learners",
    "idKey": "learner_id",
    "search": [
      {
        "key": "name",
        "label": "ชื่อ",
        "type": "text"
      },
      {
        "key": "email",
        "label": "อีเมล",
        "type": "text"
      }
    ],
    "form": [
      {
        "key": "name",
        "label": "ชื่อ",
        "type": "text"
      },
      {
        "key": "email",
        "label": "อีเมล",
        "type": "text"
      },
      {
        "key": "member_tier",
        "label": "ระดับสมาชิก",
        "type": "select",
        "options": [
          "normal",
          "vip"
        ]
      }
    ]
  },
  "courses": {
    "label": "คอร์ส",
    "api": "/api/courses",
    "idKey": "course_id",
    "search": [
      {
        "key": "title",
        "label": "ชื่อคอร์ส",
        "type": "text"
      },
      {
        "key": "category",
        "label": "หมวดหมู่",
        "type": "select",
        "options": [
          "",
          "Programming",
          "Database",
          "Design",
          "Business"
        ]
      }
    ],
    "form": [
      {
        "key": "title",
        "label": "ชื่อคอร์ส",
        "type": "text"
      },
      {
        "key": "category",
        "label": "หมวดหมู่",
        "type": "select",
        "options": [
          "Programming",
          "Database",
          "Design",
          "Business"
        ]
      },
      {
        "key": "price",
        "label": "ราคา",
        "type": "number"
      },
      {
        "key": "prerequisite_id",
        "label": "รหัสวิชาที่ต้องเรียนก่อน",
        "type": "number"
      }
    ]
  },
  "enrollments": {
    "label": "การลงทะเบียน",
    "api": "/api/enrollments",
    "idKey": "enroll_id",
    "search": [
      {
        "key": "learner_id",
        "label": "รหัสผู้เรียน",
        "type": "number"
      },
      {
        "key": "course_id",
        "label": "รหัสคอร์ส",
        "type": "number"
      },
      {
        "key": "status",
        "label": "สถานะ",
        "type": "select",
        "options": [
          "",
          "active",
          "completed",
          "dropped"
        ]
      }
    ],
    "form": [
      {
        "key": "learner_id",
        "label": "รหัสผู้เรียน",
        "type": "number"
      },
      {
        "key": "course_id",
        "label": "รหัสคอร์ส",
        "type": "number"
      },
      // [แก้ไขจุดที่ 1]: เพิ่มช่องกรอก promo_code เป็นแบบข้อความ (text)
      // หน้าที่: ให้ผู้ใช้งานสามารถพิมพ์ชื่อโค้ดส่วนลด (เช่น VIP50) ส่งไปให้ระบบหลังบ้านตรวจสอบและแปลงเป็น promo_id ได้โดยตรง
      {
        "key": "promo_code",
        "label": "โค้ดโปรโมชัน (ถ้ามี เช่น VIP50)",
        "type": "text"
      },
      {
        "key": "status",
        "label": "สถานะ",
        "type": "select",
        "options": [
          "active",
          "completed",
          "dropped"
        ]
      }
    ]
  }
};

let current = Object.keys(ENTITIES)[0];
let editingId = null;
const $ = (s) => document.querySelector(s);
function setStatus(el, msg, cls = "") { el.className = "status " + cls; el.textContent = msg; }
async function api(url, opts) { const res = await fetch(url, opts); return res.json(); }

function fieldHtml(f, prefix, value = "") {
  let input;
  if (f.type === "select") {
    input = '<select id="' + prefix + f.key + '">' +
      f.options.map(o => '<option value="' + o + '"' + (o === value ? " selected" : "") + '>' + (o || "ทั้งหมด / ไม่มี") + '</option>').join("") + '</select>';
  } else { input = '<input id="' + prefix + f.key + '" type="' + f.type + '" value="' + (value ?? "") + '">'; }
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
  $("#formFields").innerHTML = cfg.form.map(f => fieldHtml(f, "f_", data[f.key])).join("");
  $("#modal").classList.remove("hidden");
}
function collectForm() { const cfg = ENTITIES[current], d = {}; cfg.form.forEach(f => d[f.key] = $("#f_" + f.key).value); return d; }
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
  const opts = { method: editingId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) };
  const r = await api(editingId ? cfg.api + "/" + editingId : cfg.api, opts);
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



// [แก้ไข]: กำหนดให้ตัวแปร current เริ่มต้นที่ "learners" เสมอเมื่อเปิดหน้าเว็บ
// หน้าที่: บังคับให้ระบบเลือกแท็บผู้เรียนเป็นค่าเริ่มต้นก่อนเรียกฟังก์ชัน buildSearch()
current = "learners";

// [แก้ไข]: ค้นหาและทำไฮไลต์ปุ่มแท็บ "ผู้เรียน" ให้มีสถานะ active ทันทีที่โหลดหน้าเว็บ
document.querySelectorAll(".tab").forEach(t => {
  if (t.dataset.entity === "learners") t.classList.add("active");
  else t.classList.remove("active");
});


buildSearch();
setStatus($("#status"), 'กด "ค้นหา" เพื่อแสดงข้อมูล');
buildSearch();
setStatus($("#status"), 'กด "ค้นหา" เพื่อแสดงข้อมูล');