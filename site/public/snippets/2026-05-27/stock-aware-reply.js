/**
 * Stock-aware reply guard for car-dealer / property / inventory chatbots.
 * Prevents the chatbot from saying "yes we have it" when the item is
 * actually SOLD or RESERVED.
 *
 * Pattern: fetch live, never trust LLM memory for inventory.
 *
 * Usage:
 *   const reply = await stockAwareReply({
 *     query: "มี HRV ขาว ปี 2023 ไหม",
 *     fetchInventory: async (filters) => db.search(filters),
 *   });
 */

const STATUS_LABELS = {
  available: "ว่าง พร้อมนัดดู",
  reserved: "อยู่ระหว่างนัดดู — แจ้งจองได้ ถ้า lead แรกไม่ปิดดีลภายใน 24 ชม. ของคุณคิวต่อไป",
  sold: "ขายแล้ว — มีรุ่นใกล้เคียงให้ดูไหม?",
};

export async function stockAwareReply({ query, fetchInventory, parseFilters }) {
  // 1. Extract structured filters from natural-language query
  const filters = parseFilters
    ? await parseFilters(query)
    : naiveParse(query);

  // 2. Always hit live inventory — never cache "in stock?" answers
  const items = await fetchInventory(filters);

  // 3. Build deterministic reply (no LLM freelancing here)
  if (!items || items.length === 0) {
    return {
      kind: "no_match",
      text: `ขณะนี้ยังไม่มีรถตามที่หาให้ค่ะ ลองเปิดรับแจ้งเตือนเมื่อมีรถใหม่เข้ามาที่ตรงกับ ${describe(filters)} ไหมคะ?`,
    };
  }

  const available = items.filter((i) => i.status === "available");
  const reserved = items.filter((i) => i.status === "reserved");
  const sold = items.filter((i) => i.status === "sold");

  if (available.length === 0 && reserved.length === 0) {
    return {
      kind: "all_sold",
      text: "รถรุ่นที่หาขายไปแล้วทั้งหมดค่ะ — มีรุ่นใกล้เคียง 3 คันให้ดูไหม?",
      alternatives: sold.slice(0, 3).map((i) => i.alternatives || []).flat().slice(0, 3),
    };
  }

  return {
    kind: "ok",
    text: [
      `พบรถ ${available.length + reserved.length} คันค่ะ:`,
      ...available.slice(0, 5).map(
        (i) => `• ${i.label} — ${i.price.toLocaleString()} บาท · ${STATUS_LABELS.available}`,
      ),
      ...reserved.slice(0, 2).map(
        (i) => `• ${i.label} — ${i.price.toLocaleString()} บาท · ${STATUS_LABELS.reserved}`,
      ),
    ].join("\n"),
    actions: ["book_test_drive", "loan_prequal"],
  };
}

function naiveParse(q) {
  // Trivial fallback — real version uses LLM with strict JSON schema
  const yearMatch = q.match(/(20\d{2})/);
  return {
    model_keyword: q.replace(/[฀-๿]/g, "").trim(),
    year: yearMatch ? Number(yearMatch[1]) : null,
  };
}

function describe(f) {
  return [f.model_keyword, f.year].filter(Boolean).join(" ปี ");
}
