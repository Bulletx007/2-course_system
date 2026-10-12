// ============================================================
//  report.js  —  ตรรกะหน้ารายงาน (ทำให้เสร็จแล้ว ★)
// ============================================================
const $ = (s) => document.querySelector(s);
async function api(url) { return (await fetch(url)).json(); }
function fillTable(tableSel, statusSel, r) {
  const t = $(tableSel), st = $(statusSel);
  const thead = t.querySelector("thead"), tbody = t.querySelector("tbody");
  thead.innerHTML = ""; tbody.innerHTML = "";
  if (!r.ok) { st.className = "status " + (r.todo ? "todo" : "err"); st.textContent = (r.todo ? "🚧 " : "⚠️ ") + r.error; return; }
  const rows = r.data || [];
  if (!rows.length) { st.className = "status"; st.textContent = "ไม่มีข้อมูล"; return; }
  st.textContent = "";
  const cols = Object.keys(rows[0]);
  thead.innerHTML = "<tr>" + cols.map(c => "<th>" + c + "</th>").join("") + "</tr>";
  tbody.innerHTML = rows.map(row => "<tr>" + cols.map(c => "<td>" + (row[c] ?? "—") + "</td>").join("") + "</tr>").join("");
}
async function loadSummary() {
  const r = await api("/api/reports/summary");
  if (!r.ok) return;
  const d = r.data || {};
  if (d.learners !== undefined) $("#m_lrn").textContent = d.learners;
  if (d.courses !== undefined) $("#m_crs").textContent = d.courses;
  if (d.enrollments !== undefined) $("#m_enr").textContent = d.enrollments;
  if (d.lessons !== undefined) $("#m_les").textContent = d.lessons;
}
async function loadAll() {
  loadSummary();
  fillTable("#popularTable", "#popularStatus", await api("/api/reports/popular-courses"));
  fillTable("#completionTable", "#completionStatus", await api("/api/reports/completion-rate"));
  fillTable("#prereqTable", "#prereqStatus", await api("/api/reports/prerequisites"));
}
loadAll();

// ============================================================
//  [เพิ่มใหม่] โหลดรายงานการใช้งานโปรโมชัน
//  หน้าที่: เรียก API /api/reports/promotions แล้วสร้างหัวตาราง + แถวข้อมูล
//           ใส่ลงในตาราง promoReportTable ในหน้า report.html
// ============================================================
(async function loadPromoReport() {
  const st = document.getElementById("promoReportStatus");
  const table = document.getElementById("promoReportTable");
  try {
    const res = await fetch("/api/reports/promotions");
    const r = await res.json();
    if (!r.ok) { st.textContent = "⚠️ " + r.error; return; }        // ถ้าหลังบ้าน Error ให้แสดงข้อความ
    const rows = r.data || [];
    if (rows.length === 0) { st.textContent = "ยังไม่มีข้อมูลโปรโมชัน"; return; }
    const cols = Object.keys(rows[0]);                                  // ใช้ชื่อคอลัมน์จากผล SQL เป็นหัวตาราง
    table.querySelector("thead").innerHTML =
      "<tr>" + cols.map(c => "<th>" + c + "</th>").join("") + "</tr>";
    table.querySelector("tbody").innerHTML = rows.map(row =>
      "<tr>" + cols.map(c => "<td>" + (row[c] ?? "—") + "</td>").join("") + "</tr>"
    ).join("");
  } catch (e) {
    st.textContent = "⚠️ โหลดรายงานไม่สำเร็จ: " + e;
  }
})();
