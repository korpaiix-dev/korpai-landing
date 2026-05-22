// auto-service-intent-router.js
// KORP AI — intent router for car service / garage chatbot
// 5 intents: booking, parts-quote, insurance-claim, service-reminder, symptom-intake
// IMPORTANT: NEVER let AI diagnose vehicle symptoms — always escalate to mechanic
//
// Usage: const intent = await routeIntent(userMessage, customerContext);

const INTENTS = {
  BOOKING: 'booking',
  PARTS_QUOTE: 'parts-quote',
  INSURANCE_CLAIM: 'insurance-claim',
  SERVICE_REMINDER: 'service-reminder',
  SYMPTOM_INTAKE: 'symptom-intake',
  UNKNOWN: 'unknown',
};

// Thai + EN keyword heuristics — fast pre-filter before LLM
const PATTERNS = {
  [INTENTS.BOOKING]: /จอง|นัด|ว่างไหม|พรุ่งนี้|วันนี้|book|appointment|schedule|slot/i,
  [INTENTS.PARTS_QUOTE]: /ราคา|กี่บาท|เท่าไหร่|อะไหล่|ผ้าเบรก|น้ำมัน|ยาง|แบต|price|cost|how much|brake|tire|battery/i,
  [INTENTS.INSURANCE_CLAIM]: /เคลม|ชน|ประกัน|กรมธรรม์|claim|insurance|accident|damage/i,
  [INTENTS.SERVICE_REMINDER]: /ถึงรอบ|เมื่อไหร่|รอบไหน|maintenance|due|reminder|service interval/i,
  [INTENTS.SYMPTOM_INTAKE]: /เสีย|สะดุด|ดับ|ไม่ติด|มีเสียง|ผิดปกติ|ควัน|รั่ว|noise|stall|smoke|leak|won't start|engine/i,
};

// Hard guardrail: never produce a diagnosis. Always escalate.
const NEVER_DIAGNOSE = true;

async function routeIntent(message, ctx = {}) {
  for (const [intent, pattern] of Object.entries(PATTERNS)) {
    if (pattern.test(message)) {
      return {
        intent,
        confidence: 0.85,
        guardrail: intent === INTENTS.SYMPTOM_INTAKE && NEVER_DIAGNOSE
          ? 'ห้ามวินิจฉัย — รับอาการ + จองคิวให้ช่างตรวจหน้างาน'
          : null,
        next_action: nextAction(intent, ctx),
      };
    }
  }
  return { intent: INTENTS.UNKNOWN, confidence: 0.2, next_action: 'fallback_to_human' };
}

function nextAction(intent, ctx) {
  switch (intent) {
    case INTENTS.BOOKING:           return 'show_calendar_slots';
    case INTENTS.PARTS_QUOTE:       return 'extract_vehicle_then_rag_parts';
    case INTENTS.INSURANCE_CLAIM:   return 'start_claim_intake_flow_4steps';
    case INTENTS.SERVICE_REMINDER:  return 'lookup_customer_vehicle_history';
    case INTENTS.SYMPTOM_INTAKE:    return 'collect_symptoms_then_book_diagnostic';
    default:                        return 'fallback_to_human';
  }
}

module.exports = { routeIntent, INTENTS };
