/**
 * Muay Thai sparring match-score: 4-axis weighted scoring.
 * Returns a 0-1 compatibility score plus per-axis breakdown.
 *
 * Use case: bot proposes daily sparring pairings to a Line group.
 * Each fighter accepts/rejects; accepted = ring slot unlocked.
 *
 * KORP AI Automation, 2026-05-30. MIT.
 */

const WEIGHTS = { weight: 0.40, skill: 0.35, age: 0.15, intent: 0.10 };
const TOLS    = { weight: 4,    skill: 1,    age: 10,   intent: 0    };

/**
 * @param {object} a - { weight_kg, skill_1_10, age, intent: 'light'|'medium'|'hard' }
 * @param {object} b - same shape
 * @returns {{ total: number, breakdown: object, accept: boolean }}
 */
function matchScore(a, b) {
  const breakdown = {};

  // Continuous axes: linear decay from 1 -> 0 across tolerance, then clamped
  for (const axis of ['weight', 'skill', 'age']) {
    const keyA = axis === 'weight' ? 'weight_kg' : axis === 'skill' ? 'skill_1_10' : 'age';
    const diff = Math.abs(a[keyA] - b[keyA]);
    breakdown[axis] = Math.max(0, 1 - diff / TOLS[axis]);
  }
  // Intent: exact match required
  breakdown.intent = a.intent === b.intent ? 1 : 0;

  let total = 0;
  for (const k of Object.keys(WEIGHTS)) total += breakdown[k] * WEIGHTS[k];

  return { total, breakdown, accept: total >= 0.70 };
}

// Self-test
if (typeof require !== 'undefined' && require.main === module) {
  const pairs = [
    [
      { weight_kg: 70, skill_1_10: 5, age: 28, intent: 'medium' },
      { weight_kg: 72, skill_1_10: 5, age: 30, intent: 'medium' },
    ],
    [
      { weight_kg: 60, skill_1_10: 3, age: 24, intent: 'light' },
      { weight_kg: 78, skill_1_10: 9, age: 33, intent: 'hard' }, // mismatch
    ],
  ];
  for (const [a, b] of pairs) {
    console.log(JSON.stringify(matchScore(a, b), null, 2));
  }
}

module.exports = { matchScore };
