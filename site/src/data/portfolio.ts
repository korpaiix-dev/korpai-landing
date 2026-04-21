// Central data for Portfolio case personas — used by Portfolio.astro + /portfolio/[slug].astro
// NOTE: These are personas (NOT real clients) that represent the type of problems we solve.
// Numbers are illustrative — real client results vary. We respect NDA and never disclose real names.

export interface PortfolioCase {
  slug: string;
  client: string;         // persona name
  industry: string;
  metric: string;         // hero metric (e.g. "3x", "80%")
  metricLabel: string;    // short label under metric
  tagline: string;        // one-line hook for detail page hero
  note: string;           // short note on card
  gradient: string;       // CSS gradient for card cover
  emoji: string;
  img: string;            // landing card + detail hero image
  alt: string;
  challenge: string;      // 2–3 sentence problem statement
  approach: string[];     // 4–6 bullets of what we built
  outcome: Array<{ metric: string; label: string; detail: string }>; // 3–4 outcome items
  techUsed: string[];     // chips
  timeline: string;
  handoff: string;        // short sentence about what the client team runs now
  seoDesc: string;
}

export const portfolio: PortfolioCase[] = [
  {
    slug: 'fashion-line-commerce',
    client: 'พี่นิดแฟชั่น',
    industry: 'ร้านเสื้อผ้าออนไลน์',
    metric: '3x',
    metricLabel: 'ยอดขายเพิ่ม',
    tagline: 'ร้านเสื้อผ้าที่ inbox ท่วม 300+ ต่อวัน · AI ปิดการขาย 24 ชม. โดยไม่ทิ้งลูกค้าไว้ในคิว',
    note: 'ปิดการขายผ่าน AI บน Line OA · 2 เดือน',
    gradient: 'linear-gradient(135deg, #FF6B9D, #C94FFF)',
    emoji: '🛍️',
    img: 'https://images.unsplash.com/photo-1768127502130-bca3e208eba6?w=1600&auto=format&fit=crop&q=85',
    alt: 'ชั้นวางเสื้อผ้าร้านแฟชั่นสวยงามมีแสงอบอุ่น',
    challenge:
      'ร้านเสื้อผ้าที่เปิดมา 3 ปี ลูกค้า inbox วันละ 300+ message ถามสต็อก ไซส์ สี ราคา แอดมิน 2 คนตอบไม่ทัน ลูกค้ารอเกิน 30 นาทีก็หายไปซื้อร้านอื่น · เจ้าของต้องตอบ inbox ตอนตี 2 บ่อย ๆ',
    approach: [
      'AI ตอบสเปคสินค้าจากตาราง Google Sheet ของร้าน (ไซส์ สี ราคา คงเหลือ real-time)',
      'เมื่อลูกค้าสนใจ AI ขอเบอร์/ที่อยู่ + สรุปออเดอร์ส่งเข้า CRM',
      'ลูกค้าเก่า AI จำได้ว่าเคยซื้ออะไร แนะนำสไตล์ที่ match',
      'ถ้าลูกค้าถามคำถามนอกเหนือ AI ส่งต่อแอดมินพร้อม context ที่สรุปแล้ว',
      'Dashboard ให้เจ้าของดู conversation ที่ AI ไม่แน่ใจ เพื่อปรับ prompt ต่อ',
    ],
    outcome: [
      { metric: '3x', label: 'ยอดขาย Line', detail: 'จาก 200k → 600k/เดือน ในไตรมาสแรก' },
      { metric: '< 10s', label: 'เวลาตอบ', detail: 'จากเดิมเฉลี่ย 18 นาที เหลือต่ำกว่า 10 วินาที' },
      { metric: '0', label: 'Inbox ตอนตี 2', detail: 'เจ้าของกลับมานอนปกติ ทีมใช้เวลาทำคอนเทนต์แทน' },
    ],
    techUsed: ['Claude 3.5 Sonnet', 'Line OA API', 'Google Sheets', 'n8n', 'Airtable CRM'],
    timeline: '2 สัปดาห์ build + 2 สัปดาห์ tuning',
    handoff: 'เจ้าของร้านจัดการ Google Sheet สินค้าได้เอง · AI เรียนรู้ต่ออัตโนมัติ',
    seoDesc: 'AI Chatbot สำหรับร้านเสื้อผ้าออนไลน์ · ตอบ inbox 300+ ต่อวัน · ปิดการขาย 24 ชม. · ยอดขายเพิ่ม 3x ใน 2 เดือน',
  },
  {
    slug: 'thai-restaurant-booking',
    client: 'ครัวคุณยาย',
    industry: 'ร้านอาหารไทย',
    metric: '80%',
    metricLabel: 'จองโต๊ะผ่าน AI',
    tagline: 'ร้านอาหารไทยกลางเมืองที่โทรรับจองไม่ทัน · AI รับจองโต๊ะได้ 24 ชม. ระบบคิวไม่หลุด',
    note: 'จองโต๊ะอัตโนมัติ + จัดการคิวหน้าร้าน',
    gradient: 'linear-gradient(135deg, #FF9A3C, #FF3C3C)',
    emoji: '🍜',
    img: 'https://images.unsplash.com/photo-1758346970538-40d665b0afa0?w=1600&auto=format&fit=crop&q=85',
    alt: 'เมนูอาหารไทยร้อน ๆ พร้อมเสิร์ฟบนโต๊ะไม้',
    challenge:
      'ร้านอาหารไทย 80 ที่นั่ง เสาร์-อาทิตย์เต็มตลอด ลูกค้าโทรจองแต่พนักงานหน้าร้านรับไม่ทัน บางช่วงพลาดโทรถึง 40% · ลูกค้า walk-in รอ 40 นาทีแล้วไปร้านอื่น · ระบบคิวเป็นกระดาษหลุดบ่อย',
    approach: [
      'AI รับจองโต๊ะบน Line OA + Messenger — เลือกวัน/เวลา/จำนวนคน/preferred seat',
      'Sync กับ Google Calendar ร้าน · AI เช็ค capacity real-time',
      'Walk-in คิวผ่าน QR หน้าร้าน · ลูกค้าเห็นคิวปัจจุบัน + เวลาประเมิน',
      'Reminder 1 ชม. ก่อนนัด ลด no-show จาก 25% → 8%',
      'AI รู้เมนูขายดี แนะนำ pre-order ขณะจอง ช่วยทีมครัวเตรียม',
    ],
    outcome: [
      { metric: '80%', label: 'จองผ่าน AI', detail: 'จากเดิมโทร 100% ตอนนี้ 80% ผ่าน AI · โทรเหลือแค่ลูกค้าสูงอายุ' },
      { metric: '–17%', label: 'No-show', detail: 'จาก 25% → 8% เพราะมี reminder อัตโนมัติ' },
      { metric: '+15%', label: 'Avg ticket', detail: 'AI แนะนำเมนู pre-order ระหว่างจอง ช่วยเพิ่มยอดต่อโต๊ะ' },
    ],
    techUsed: ['Claude 3.5 Sonnet', 'Line OA API', 'Google Calendar API', 'n8n', 'Airtable'],
    timeline: '3 สัปดาห์',
    handoff: 'พนักงานหน้าร้านใช้แท็บเล็ตดู dashboard จองของวันนั้น · ปรับ capacity ได้เอง',
    seoDesc: 'AI Booking System สำหรับร้านอาหารไทย · รับจองโต๊ะอัตโนมัติ 24 ชม. · ลด no-show · เพิ่มยอดขายต่อโต๊ะ',
  },
  {
    slug: 'derma-clinic-admin',
    client: 'Derma Clinic BKK',
    industry: 'คลินิกผิวหนัง',
    metric: '70%',
    metricLabel: 'ลดงาน admin',
    tagline: 'คลินิกผิวหนังที่มีแพทย์ 3 ท่าน · ลูกค้าเยอะ · แอดมินเคยทำงาน reminder + จองคิวจนไม่มีเวลาดูแลลูกค้าตรงหน้า',
    note: 'จองคิวหมอ + ส่งแผนที่ + เตือนก่อนวันนัด',
    gradient: 'linear-gradient(135deg, #26D7F6, #3C7CFF)',
    emoji: '🏥',
    img: 'https://images.unsplash.com/photo-1758691462123-8a17ae95d203?w=1600&auto=format&fit=crop&q=85',
    alt: 'เคาน์เตอร์คลินิกความงามสมัยใหม่สะอาดตา',
    challenge:
      'คลินิกมี 3 แพทย์ · ตารางหมอแต่ละคนไม่เหมือนกัน · แอดมิน 2 คนใช้เวลา 4+ ชม./วันแค่โทร reminder นัดหมาย + ตอบคำถามเรื่องราคาทรีตเมนต์ซ้ำ ๆ · ลูกค้า walk-in รอนานเพราะแอดมินไม่ว่าง',
    approach: [
      'AI รับคำถามราคา + tritment แนะนำผ่าน Line OA — ตอบจาก catalogue จริงของคลินิก',
      'จองคิวตามตารางแพทย์ใน Google Calendar · AI รู้ว่า tritment นี้ควรใช้กับหมอคนไหน',
      'Reminder อัตโนมัติ 24 ชม. + 2 ชม. ก่อนนัด · ส่งแผนที่ + คู่มือเตรียมตัว',
      'หลังทรีตเมนต์ AI follow-up "ผลเป็นยังไงบ้าง?" + ถามว่าจองครั้งต่อไปเลยไหม',
      'ข้อมูลลูกค้าเข้ารหัส PDPA compliance · audit log ทุก access',
    ],
    outcome: [
      { metric: '–70%', label: 'งาน admin', detail: 'แอดมินเหลือเวลา 4 ชม./วัน กลับไปดูแลลูกค้าหน้าเคาน์เตอร์' },
      { metric: '+35%', label: 'Re-booking rate', detail: 'Follow-up อัตโนมัติช่วยให้ลูกค้ากลับมาบ่อยขึ้น' },
      { metric: '< 5 นาที', label: 'เวลาจอง', detail: 'จากเดิมต้องโทรเช็คตารางหมอ 10–15 นาที' },
    ],
    techUsed: ['Claude 3.5 Sonnet', 'Line OA API', 'Google Calendar', 'pgvector (RAG)', 'n8n', 'PDPA-compliant storage'],
    timeline: '4 สัปดาห์ (includes PDPA audit)',
    handoff: 'แอดมินจัดการ catalogue tritment เอง · ข้อมูลลูกค้าอยู่บน server ไทย · export ได้ 100%',
    seoDesc: 'AI + Automation สำหรับคลินิกผิวหนัง · จองคิวหมอ · ส่ง reminder · PDPA compliance · ลดงาน admin 70%',
  },
  {
    slug: 'it-gadget-shop',
    client: 'BKK Gadgets',
    industry: 'ร้าน IT Online',
    metric: '5x',
    metricLabel: 'ตอบลูกค้าเร็วขึ้น',
    tagline: 'ร้านขาย gadget ออนไลน์ 1,200+ SKU · ลูกค้าถามสเปคซับซ้อน · AI ตอบได้เหมือน sales engineer',
    note: 'AI ตอบสเปค + แนะนำสินค้า + เช็คสต็อก',
    gradient: 'linear-gradient(135deg, #7C5FFF, #3C7CFF)',
    emoji: '💻',
    img: 'https://images.unsplash.com/photo-1513258496099-48168024aec0?w=1600&auto=format&fit=crop&q=85',
    alt: 'อุปกรณ์ IT gadgets วางเรียงบนโต๊ะทำงาน',
    challenge:
      'ร้านขาย gadget 1,200+ SKU — notebook, mechanical keyboard, camera gear · ลูกค้าถามสเปคละเอียด ("compatibility เคสกับ mobo นี้ได้ไหม?" "RAM 3200MHz กับ CPU นี้คุ้มกว่า 3600?") · ทีมขาย 3 คนต้องเปิด spec sheet ทุกครั้ง · เสียลูกค้าเพราะตอบช้า',
    approach: [
      'AI โหลดสเปคสินค้า 1,200 SKU เข้า RAG database · ตอบคำถาม compatibility ได้เอง',
      'เช็คสต็อกจากระบบ POS real-time · "ตอนนี้เหลือ 3 ตัว ที่สาขาสยาม"',
      'แนะนำ "คู่สินค้า" ที่ compatible · "ซื้อ CPU นี้แนะนำ cooler นี้ด้วย"',
      'เห็นคำถามที่ AI ตอบไม่ได้ → ทีมเพิ่ม FAQ → AI เรียนรู้ต่อ',
      'Integration กับ Shopee/Lazada chat · ตอบเหมือนกันทุก channel',
    ],
    outcome: [
      { metric: '5x', label: 'ตอบเร็วขึ้น', detail: 'จาก avg 5 นาที → < 1 นาที · ลูกค้ายอมรอเพราะตอบลึก' },
      { metric: '+40%', label: 'Conversion', detail: 'ปิดการขายได้มากขึ้นเพราะ AI แนะนำสินค้า match กับ use case' },
      { metric: '0', label: 'เคสโทรถาม', detail: 'ลูกค้าไม่โทรมาถามสเปคเลย · ทีมขายไปโฟกัสปิดดีลใหญ่' },
    ],
    techUsed: ['Claude 3.5 Sonnet', 'pgvector (RAG)', 'Line OA', 'Shopee API', 'Lazada API', 'POS webhook'],
    timeline: '3 สัปดาห์',
    handoff: 'ทีมอัปเดตสเปคใน Google Sheet · sync อัตโนมัติเข้า RAG ทุกชั่วโมง',
    seoDesc: 'AI Sales Assistant สำหรับร้าน IT · ตอบสเปคสินค้า 1,200 SKU · เช็คสต็อก real-time · conversion +40%',
  },
  {
    slug: 'wellness-spa-booking',
    client: 'Pure Wellness',
    industry: 'สปา & Wellness',
    metric: '24/7',
    metricLabel: 'จองคิว auto',
    tagline: 'สปาที่ลูกค้าอยากจองตอน 5 ทุ่ม แต่พนักงานเลิก 8 โมง · AI รับจองได้ตลอดไม่พลาดลูกค้ากลางคืน',
    note: 'ลูกค้าจองได้ตอนร้านปิด · เพิ่มยอด 40%',
    gradient: 'linear-gradient(135deg, #22C55E, #26D7F6)',
    emoji: '🌿',
    img: 'https://images.unsplash.com/photo-1709755491926-f7aa83748967?w=1600&auto=format&fit=crop&q=85',
    alt: 'ห้องสปาสวยสงบมีไฟอบอุ่นและดอกไม้',
    challenge:
      'สปา wellness ที่ลูกค้าเป้าหมายเป็นผู้บริหาร · เลิกงาน 2-3 ทุ่มถึงนึกอยากจอง · ร้านปิด 2 ทุ่ม admin ไม่อยู่ตอบ · อีกวันลูกค้าลืมหรือจองร้านอื่นไปแล้ว · พลาดโอกาส 30%+',
    approach: [
      'AI รับจองผ่าน Line OA + Messenger ตลอด 24 ชม.',
      'แนะนำ package ตาม preferences ลูกค้าเคยจอง (60 นาที / 90 นาที / aromatherapy)',
      'Confirm ทันที + reminder 24 ชม. + send แผนที่',
      'ระบบ loyalty · ลูกค้าจอง 5 ครั้งได้ 1 ครั้งฟรี · AI ติดตามเอง',
      'Gift voucher purchase ผ่าน chat · ส่ง digital voucher auto',
    ],
    outcome: [
      { metric: '+40%', label: 'ยอดจอง', detail: 'ส่วนใหญ่เป็นการจองช่วง 21:00–02:00 น.' },
      { metric: '+60%', label: 'Gift voucher', detail: 'ซื้อผ่าน chat ตอนเย็น · โอนแล้วเสร็จใน 3 นาที' },
      { metric: '< 30s', label: 'จอง completion', detail: 'จากเริ่มคุย → ยืนยันจอง · เร็วกว่าเปิดแอปจองทั่วไป' },
    ],
    techUsed: ['Claude 3.5 Sonnet', 'Line OA API', 'Google Calendar', 'Stripe (voucher)', 'n8n'],
    timeline: '2 สัปดาห์',
    handoff: 'เจ้าของดู calendar · แก้ capacity/pricing ใน Google Sheet · AI ตาม',
    seoDesc: 'AI Booking 24 ชม. สำหรับสปา · รับจองช่วงลูกค้าคิดจะจอง (ตอนกลางคืน) · ยอดจองเพิ่ม 40%',
  },
  {
    slug: 'specialty-coffee-upsell',
    client: 'Brew & Co',
    industry: 'ร้านกาแฟ Specialty',
    metric: '+25%',
    metricLabel: 'Upsell เมนู',
    tagline: 'ร้านกาแฟ specialty ที่อยาก upsell เมนู pairing แต่ไม่มี budget จ้าง barista counter เพิ่ม · AI ทำแทนบน Line',
    note: 'AI แนะนำเมนูเด็ด + โปรมาคู่กับเค้ก',
    gradient: 'linear-gradient(135deg, #D4A574, #8B4513)',
    emoji: '☕',
    img: 'https://images.unsplash.com/photo-1774014045872-3cc2b5e7e816?w=1600&auto=format&fit=crop&q=85',
    alt: 'กาแฟ specialty ที่ชงเสร็จใหม่ในแก้วสวย',
    challenge:
      'ร้านกาแฟ specialty 3 สาขา · เจ้าของอยากให้ลูกค้ารู้จักเมนู pairing (เช่น Ethiopian + orange cake) แต่ counter ไม่มีเวลาอธิบาย · website/menu board อ่านผ่าน · อยากเพิ่ม avg ticket โดยไม่เพิ่มคน',
    approach: [
      'AI ตอบใน Line OA · ให้ลูกค้าเลือกเมนูกาแฟ → แนะนำเค้ก/ขนม pairing',
      'AI อธิบาย flavor notes + origin ของ bean วันนี้',
      'Pre-order ผ่าน chat · ลูกค้ามาถึงกาแฟพร้อม · ไม่ต้องรอคิว',
      'Loyalty stamp auto · ซื้อ 10 แก้วฟรี 1 · AI บอกลูกค้าเหลือกี่แก้ว',
      'แจ้ง bean ใหม่อาทิตย์ไหน · ลูกค้าขา regular รู้ก่อน',
    ],
    outcome: [
      { metric: '+25%', label: 'Avg ticket', detail: 'ลูกค้าที่คุยกับ AI ซื้อกาแฟ + เค้ก/ขนมร่วมด้วย 60%' },
      { metric: '+18%', label: 'Return rate', detail: 'Loyalty stamp + bean alert ทำให้ลูกค้ากลับมาบ่อยขึ้น' },
      { metric: '3 min', label: 'Save time/order', detail: 'Pre-order ตัดเวลา queue 3 นาที/ลูกค้า · ระบบคิวดีขึ้น' },
    ],
    techUsed: ['Claude 3.5 Sonnet', 'Line OA API', 'POS webhook', 'n8n', 'Google Sheets'],
    timeline: '2 สัปดาห์',
    handoff: 'barista อัปเดตเมนู/bean ใน Google Sheet · AI รู้ทันที · ไม่ต้องแก้ code',
    seoDesc: 'AI Upsell + Pre-order สำหรับร้านกาแฟ specialty · แนะนำเมนู pairing · loyalty auto · avg ticket +25%',
  },
];

export const getCaseBySlug = (slug: string) => portfolio.find((c) => c.slug === slug);
