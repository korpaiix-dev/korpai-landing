// Central data for Services — used by landing Services.astro + /services/[slug].astro
// Add/modify services here; both the landing section and detail page reflect changes automatically.

export interface Service {
  slug: string;
  tag: string;           // short category chip shown on card
  title: string;         // page title + card H3
  shortDesc: string;     // one-liner for landing card
  tagline: string;       // hero sub-line for detail page
  img: string;           // landing card + detail hero image
  alt: string;
  highlights: string[];  // 4–6 bullet highlights
  whoFor: string[];      // 3–5 bullets of "who this is for"
  useCases: Array<{ title: string; desc: string }>; // 3–4 concrete use cases
  workflow: Array<{ step: string; detail: string }>; // 3–4 steps of how we deliver
  tech: string[];        // chip-style tech/tools stack
  timeline: string;      // plain string e.g. "1–2 สัปดาห์"
  seoDesc: string;       // short meta description
}

export const services: Service[] = [
  {
    slug: 'ai-chatbot',
    tag: 'Chatbot',
    title: 'AI Sales Agent',
    shortDesc: 'ตอบแชทลูกค้า 24 ชม. บน Line OA, Messenger, เว็บ — คัดกรอง, จองคิว, ส่งต่อทีมขาย',
    tagline: 'AI ตอบลูกค้าเหมือนแอดมินตัวจริง เรียนรู้จากข้อมูลของธุรกิจคุณ ไม่ใช่ bot สคริปต์ตายตัว',
    img: '/assets/img/ai-chatbot.jpg',
    alt: 'บาริสต้าไทยในคาเฟ่ ใช้มือถือตอบลูกค้าผ่าน AI Chatbot มีแชทบับเบิลลอยอยู่หน้าจอ',
    highlights: [
      'รองรับ Line OA, Facebook Messenger, Web Chat ในตัวเดียว',
      'ตอบจากฐานความรู้ของธุรกิจ (RAG) — ไม่เดา ไม่มั่ว',
      'คัดกรองลูกค้า hot/warm/cold ส่งต่อทีมขายตามเกณฑ์',
      'รู้เวลาที่ต้องเงียบแล้วส่งต่อคนจริง — ไม่กลบทีม',
      'log ทุกบทสนทนา มี dashboard ดู pattern + ปรับต่อได้',
      'พูดไทยเข้าใจเนียน อ่านสำเนียง อีสาน/เหนือ/ใต้ + emoji ได้',
    ],
    whoFor: [
      'ร้านอาหาร/คาเฟ่ที่ลูกค้า inbox เยอะ มีคำถามซ้ำ',
      'คลินิก/สปาที่ต้องจองคิว + ส่ง reminder',
      'ร้านออนไลน์ที่ขายของผ่าน Line/FB มีลูกค้าถามสเปค',
      'ธุรกิจบริการ (ที่ปรึกษา, โรงเรียนกวดวิชา) ที่ลูกค้า qualify ยาก',
    ],
    useCases: [
      { title: 'รับจองโต๊ะ/คิว', desc: 'ลูกค้าเลือกวัน-เวลา-จำนวนคน AI เช็คคิวว่างไหม ยืนยันทันที พร้อมส่งเข้า Google Sheet ทีมหน้าร้าน' },
      { title: 'ตอบคำถาม FAQ', desc: 'เวลาเปิดปิด ที่อยู่ เมนู ราคา โปร นโยบายคืน — ตอบจากข้อมูลจริงของร้าน ไม่เดา' },
      { title: 'คัดกรอง Lead', desc: 'ถามลูกค้าว่าสนใจแพ็กเกจไหน งบเท่าไหร่ ติดต่อกลับช่วงไหน — สรุปส่งทีมขายพร้อมปิด' },
      { title: 'Upsell อัตโนมัติ', desc: 'ลูกค้าสั่งกาแฟ AI แนะนำเค้กคู่ + โปรซื้อคู่ลด 20% conversion เพิ่มโดยไม่ต้องจ้าง upseller' },
    ],
    workflow: [
      { step: 'คุยโจทย์ + เก็บข้อมูล', detail: 'สัมภาษณ์ทีม ฟัง pain point + รวบรวมเมนู/สินค้า/FAQ เป็นฐานความรู้' },
      { step: 'สร้าง prototype', detail: 'ติดตั้งระบบกับ Line OA/Messenger/เว็บภายใน 7–10 วัน ทดสอบ 30+ บทสนทนาจริง' },
      { step: 'soft launch + ปรับ tone', detail: 'เปิดให้ลูกค้าประจำลองก่อน เก็บ log จริง ปรับ prompt ให้ tone ตรงแบรนด์' },
      { step: 'ส่งมอบ + ดูแล', detail: 'ส่งคู่มือ + training ทีม · ดูแลรายเดือน ปรับตามคำถามใหม่ที่เจอ' },
    ],
    tech: ['Claude 3.5 Sonnet', 'GPT-4o', 'Line Official API', 'Messenger API', 'pgvector (RAG)', 'n8n', 'Google Sheets'],
    timeline: '1–3 สัปดาห์',
    seoDesc: 'AI Sales Agent ที่ตอบลูกค้าบน Line OA, Messenger, เว็บ แบบ 24 ชม. · คัดกรองลีด · ส่งต่อทีมขาย · ใช้ RAG ตอบจากข้อมูลจริงของธุรกิจ ไม่เดา',
  },
  {
    slug: 'automation',
    tag: 'Automation',
    title: 'Workflow Automation',
    shortDesc: 'ต่อระบบที่ทีมใช้ — Form → Sheet → CRM → Line แจ้งทีม ประหยัดเวลางานซ้ำ ๆ ที่ไม่จำเป็น',
    tagline: 'ตัดงาน copy-paste 40+ ชม./เดือน ทีมไปโฟกัสงานที่สำคัญกว่าแทนการกรอกข้อมูลซ้ำ',
    img: 'https://images.unsplash.com/photo-1758691737083-0e7fdbde0f05?w=1600&auto=format&fit=crop&q=85',
    alt: 'พนักงานสองคนทำงานร่วมกันหน้าจอ automation',
    highlights: [
      'เชื่อม Facebook Lead Ads → CRM → Line กลุ่มทีมขายใน 2 นาที',
      'สร้างใบเสนอราคา + ส่งเมลอัตโนมัติจาก Line chat',
      'Sync ออเดอร์ Shopee/Lazada → ปริ้น label → แจ้งแพ็ค',
      'สรุปรีวิวลูกค้าทุกสัปดาห์ ส่งเมลผู้บริหาร',
      'Reminder นัดหมายลดการ no-show 50–70%',
      'มี log + ปุ่ม pause ทุก flow — ถ้าผิดหยุดได้ก่อนส่งผิด 500 คน',
    ],
    whoFor: [
      'ธุรกิจที่ยิง Facebook/Google Ads แต่ลีดหายเพราะไม่มีใครตาม',
      'ร้านออนไลน์ขายหลาย platform (Shopee + Lazada + Line)',
      'คลินิก/สถานเสริมความงามที่ต้องจัดการนัดเยอะ',
      'ที่ปรึกษา/freelancer ที่เสียเวลาทำใบเสนอราคาเอง',
    ],
    useCases: [
      { title: 'Lead Ads → Line ทีมขาย', desc: 'ลูกค้ากรอก Lead Form บน Facebook → ข้อมูลเข้า Sheet + ping Line ทีมในไม่ถึง 2 นาที ปิดลีด hot ได้ทันที' },
      { title: 'Order → Packing', desc: 'ออเดอร์ Shopee/Lazada → สร้าง PDF label → ส่ง printer + แจ้งทีมแพ็ค ลดเวลาเตรียมของ 70%' },
      { title: 'ใบเสนอราคาอัตโนมัติ', desc: 'ลูกค้าคุยใน Line → AI สรุป spec → gen PDF + ส่งเมล + ลิงก์ยืนยันใน 5 นาที' },
      { title: 'Reminder นัดหมาย', desc: 'Google Calendar → Line reminder 24 ชม. + 1 ชม. ก่อนนัด · ลูกค้า cancel เองได้ · คิวว่าง release ให้คนอื่น' },
    ],
    workflow: [
      { step: 'Audit workflow ปัจจุบัน', detail: 'นั่งดูทีมทำงาน 1 วัน จับจุดที่เสียเวลามากสุด — ไม่ใช่ flow ที่ "เท่สุด"' },
      { step: 'เลือก 1–2 flow ที่ ROI สูงสุด', detail: 'คำนวณเวลา/เดือนที่ประหยัด vs cost เริ่มต้น ทำ flow ที่คุ้มสุดก่อน' },
      { step: 'Build + test + soft launch', detail: 'Build ใน n8n/Make ทดสอบกับทีมจริง 1 สัปดาห์ก่อน launch' },
      { step: 'ดูแล + ขยาย', detail: 'รัน flow + log รายเดือน · เจอ flow ใหม่ที่ควร automate ทำเพิ่ม' },
    ],
    tech: ['n8n', 'Make.com', 'Zapier', 'Google Apps Script', 'Facebook Lead Ads API', 'Shopee/Lazada API', 'Line Notify'],
    timeline: '2–4 สัปดาห์',
    seoDesc: 'Workflow Automation สำหรับ SME ไทย — เชื่อม Lead Ads, CRM, Line, Shopee, Lazada อัตโนมัติ · คืนเวลาทีม 40+ ชม./เดือน',
  },
  {
    slug: 'dashboard',
    tag: 'Dashboard',
    title: 'Realtime Dashboard',
    shortDesc: 'แดชบอร์ดยอดขาย ลีด KPI real-time จากระบบเดิม ทีมดูได้ทั้ง desktop และมือถือ',
    tagline: 'เห็นตัวเลขสำคัญของธุรกิจใน 10 วินาที ไม่ต้อง login 3 platforms แล้วคำนวณในหัว',
    img: 'https://images.unsplash.com/photo-1763718528755-4bca23f82ac3?w=1600&auto=format&fit=crop&q=85',
    alt: 'แดชบอร์ดข้อมูลแสดงเทรนด์และตัวชี้วัดสำคัญบนหน้าจอคอมพิวเตอร์',
    highlights: [
      'ดึงข้อมูลจาก Shopee, Lazada, Line Ads, Google Sheet, Postgres รวมที่เดียว',
      'เลือก tool ที่เหมาะ — Grafana (realtime), Metabase (ง่าย), Power BI (Excel-first)',
      'Responsive — ผู้บริหารดูบนมือถือได้ขณะประชุม',
      'ส่ง report email รายวัน/สัปดาห์อัตโนมัติ',
      'กราฟเทียบ period ก่อนหน้า + alert เมื่อ KPI ผิดปกติ',
      'User permission — ทีมขายดูยอดตัวเอง ผู้บริหารดูภาพรวม',
    ],
    whoFor: [
      'ผู้บริหาร SME ที่อยาก "เห็นภาพรวม" โดยไม่ต้องเปิด Excel 3 ไฟล์',
      'ทีมขายที่ต้องรู้ว่า KPI ตัวเองอยู่ตรงไหนทุกวัน',
      'ธุรกิจขายหลายช่องทางอยากเทียบ performance',
      'สตาร์ทอัพที่ต้องโชว์ investor ตัวเลข realtime',
    ],
    useCases: [
      { title: 'ยอดขาย realtime', desc: 'เห็นยอดวันนี้ · เทียบวันเดียวกันเดือนที่แล้ว · breakdown by ช่อง (Shopee/Lazada/Line)' },
      { title: 'ลีด funnel', desc: 'Lead Ads → CRM → นัด → ปิด · รู้ว่าหล่นจุดไหน · conversion rate ทีมขายแต่ละคน' },
      { title: 'สต็อก alert', desc: 'สินค้าไหนเหลือ < 10 · สั่งใหม่ล่วงหน้า · ไม่ต้องรอคนเช็ค Excel' },
      { title: 'Ad spend ROI', desc: 'Facebook/Google Ads cost vs revenue ต่อแคมเปญ · ตัดแคมเปญขาดทุนเร็ว' },
    ],
    workflow: [
      { step: 'เลือก tool ให้เหมาะ', detail: 'Grafana สำหรับ realtime · Metabase สำหรับทีม non-tech · Power BI สำหรับ Microsoft shop' },
      { step: 'เชื่อม data source', detail: 'ต่อ Shopee/Lazada/Google Sheet/Postgres เข้า tool เดียว · Setup ETL pipeline' },
      { step: 'ออกแบบ dashboard', detail: 'วาง layout ให้เห็นตัวเลขสำคัญก่อน · ไม่ใส่กราฟที่ไม่ถูกใช้' },
      { step: 'Training + report auto', detail: 'สอนทีม · ตั้งระบบส่ง report email รายสัปดาห์ให้ผู้บริหาร' },
    ],
    tech: ['Grafana', 'Metabase', 'Power BI', 'Postgres', 'Google BigQuery', 'Shopee API', 'Lazada API', 'Python ETL'],
    timeline: '2–4 สัปดาห์',
    seoDesc: 'Realtime Dashboard สำหรับ SME — รวมยอดขาย ลีด KPI จากทุก platform ใช้ Grafana/Metabase/Power BI · มือถือใช้ได้ · report email อัตโนมัติ',
  },
  {
    slug: 'custom-ai',
    tag: 'Custom AI',
    title: 'Custom AI Feature',
    shortDesc: 'สรุปเอกสาร, ตอบจากฐานความรู้ภายใน, สร้างภาพ หรือระบบเสียง ออกแบบตามโจทย์ทีมคุณ',
    tagline: 'โจทย์พิเศษที่ไม่มี SaaS ไหน solve ให้ได้ — เราออกแบบระบบ AI ตามโจทย์จริงของธุรกิจคุณ',
    img: 'https://images.unsplash.com/photo-1758876202014-6b2062bed4e8?w=1600&auto=format&fit=crop&q=85',
    alt: 'พนักงานผู้หญิงใช้ AI feature บนโน้ตบุ๊กในออฟฟิศโมเดิร์น',
    highlights: [
      'RAG เชื่อมเอกสารภายในบริษัท (สัญญา, manual, SOP)',
      'สรุปมีตติ้ง/เสียงเป็นข้อความ + action items',
      'Voice AI สำหรับ call center — ตอบลูกค้าทางโทรศัพท์',
      'Image generation ตามแบรนด์ (สินค้า, โฆษณา, thumbnail)',
      'OCR + เข้าใจใบเสร็จ/ใบกำกับภาษี/ใบสั่งซื้อ',
      'Integration กับ ERP/POS/CRM ของบริษัท',
    ],
    whoFor: [
      'บริษัทที่มีเอกสารภายในเยอะ พนักงานหาไม่เจอ',
      'ทีมขายที่ประชุมเยอะ ต้องการสรุป + action item อัตโนมัติ',
      'Call center ที่รับสายเยอะ ต้องการ AI รับสายชั้นแรก',
      'ธุรกิจที่ process document เยอะ (บัญชี, legal, logistics)',
    ],
    useCases: [
      { title: 'RAG เอกสารบริษัท', desc: 'Upload นโยบาย/สัญญา/SOP → พนักงานถามภาษาธรรมชาติได้ "นโยบายลาเรื่องนี้เป็นยังไง" ตอบพร้อมอ้างอิง section' },
      { title: 'สรุปมีตติ้งอัตโนมัติ', desc: 'อัด Zoom/Google Meet → AI transcribe + สรุป + แตก action item + ส่งเข้า Slack/Line' },
      { title: 'Voice AI รับสาย', desc: 'ลูกค้าโทรเข้า AI ตอบคำถามชั้นแรก · ถ้าซับซ้อน transfer คน · พูดไทยเนียน' },
      { title: 'OCR ใบเสร็จ', desc: 'สแกนใบกำกับภาษี → AI extract ข้อมูล → เข้าระบบบัญชีอัตโนมัติ ลดงาน accountant 70%' },
    ],
    workflow: [
      { step: 'Deep dive โจทย์', detail: 'workshop 2–3 ชม. กับ stakeholder เข้าใจโจทย์จริง ไม่ใช่ surface requirement' },
      { step: 'PoC 2 สัปดาห์', detail: 'สร้าง prototype จริงกับข้อมูลตัวอย่าง · วัด accuracy + รับ feedback' },
      { step: 'Production build', detail: 'Scale ขึ้น production · เชื่อม ERP/CRM · security review · PDPA compliance' },
      { step: 'Handoff + SLA', detail: 'Training ทีม + เอกสาร + SLA support · dedicated engineer สำหรับ Enterprise' },
    ],
    tech: ['Claude 3.5 Sonnet', 'GPT-4o', 'Gemini 1.5 Pro', 'Whisper (speech)', 'Vision API', 'pgvector', 'LangGraph', 'Custom Python'],
    timeline: '4–12 สัปดาห์',
    seoDesc: 'Custom AI Feature สำหรับองค์กร — RAG เอกสารภายใน, สรุปประชุม, voice AI, OCR · integration ERP/CRM · PDPA compliance',
  },
];

export const getServiceBySlug = (slug: string) => services.find((s) => s.slug === slug);
