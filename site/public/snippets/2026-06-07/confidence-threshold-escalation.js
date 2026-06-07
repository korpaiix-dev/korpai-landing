// confidence-threshold-escalation.js
// Handoff trigger #2 + #3: escalate after repeated low-confidence / failed answers.
// Rule of thumb: 2 weak answers in a row -> offer a human on the 3rd turn.
// Track per-conversation state; pure function + tiny state machine.
// KORP AI — https://korpai.co/blog/ai-chatbot-human-handoff-ส่งต่อเจ้าหน้าที่-sme-ไทย-2026

function createEscalationTracker({ minConfidence = 0.55, maxWeakTurns = 2 } = {}) {
  let weakStreak = 0;
  return {
    /**
     * Call after every bot turn.
     * @param {number} confidence 0..1 retrieval/answer confidence
     * @param {boolean} hadSource did RAG return a citable source?
     * @returns {{escalate:boolean, reason:string|null}}
     */
    record(confidence, hadSource = true) {
      const weak = confidence < minConfidence || !hadSource;
      weakStreak = weak ? weakStreak + 1 : 0;
      if (weakStreak > maxWeakTurns) {
        return { escalate: true, reason: `low_confidence_x${weakStreak}` };
      }
      return { escalate: false, reason: null };
    },
    reset() { weakStreak = 0; },
    get streak() { return weakStreak; },
  };
}

if (require.main === module) {
  const t = createEscalationTracker();
  [[0.9, true], [0.4, true], [0.3, false], [0.2, false]].forEach(([c, s], i) =>
    console.log(`turn ${i + 1}: conf=${c} ->`, t.record(c, s)));
}

module.exports = { createEscalationTracker };
