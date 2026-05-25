// line-onboard-doc-checklist.js — Onboarding doc checklist for accounting clients
// over LINE OA. Reduces onboarding from 4-8 hrs → 30 min by guiding the client
// through an ordered, per-stage upload (with PDPA consent gate).
// KORP AI · 2026 · MIT

const STAGES = [
  { id: "consent", required: ["pdpa_consent_signed"], hint: "ส่งใบยินยอม PDPA (กดปุ่มเซ็น)" },
  { id: "identity", required: ["company_certificate", "vat_registration_pp20", "id_card_director"], hint: "หนังสือรับรอง 30 วัน + ภพ.20 + บัตร ปชช. กรรมการ" },
  { id: "history",  required: ["bank_statement_3mo", "previous_pp30_3mo"], hint: "Statement 3 เดือน + ภพ.30 3 เดือนล่าสุด" },
  { id: "ops",      required: ["customer_list", "vendor_list", "employee_list"], hint: "รายชื่อลูกค้า/ผู้ขาย/พนักงาน (Excel หรือ Sheet link)" },
  { id: "assets",   required: ["fixed_asset_register"], hint: "ทะเบียนทรัพย์สิน (ถ้ามี)" }
];

function nextMissing(uploadedDocs) {
  for (const stage of STAGES) {
    const missing = stage.required.filter(d => !uploadedDocs.includes(d));
    if (missing.length) {
      return { stage: stage.id, hint: stage.hint, missing };
    }
  }
  return null;
}

function buildLineFlex(next) {
  if (!next) {
    return { type: "text", text: "✅ เอกสาร onboarding ครบแล้ว — สำนักงานจะติดต่อกลับใน 24 ชม." };
  }
  return {
    type: "flex",
    altText: `ยังต้อง upload ${next.missing.length} ไฟล์`,
    contents: {
      type: "bubble",
      body: { type: "box", layout: "vertical", contents: [
        { type: "text", text: `Stage ${next.stage}`, weight: "bold", size: "lg" },
        { type: "text", text: next.hint, wrap: true, margin: "md" },
        { type: "text", text: `ขาด: ${next.missing.join(", ")}`, color: "#aa0000", margin: "md", wrap: true }
      ]}
    }
  };
}

module.exports = { STAGES, nextMissing, buildLineFlex };
