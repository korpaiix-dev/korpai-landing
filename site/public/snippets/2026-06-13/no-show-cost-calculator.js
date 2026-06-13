// no-show-cost-calculator.js
// คำนวณต้นทุน no-show ต่อเดือน + รายได้ที่กู้คืนได้ ถ้าลด no-show ลง
// ใช้กับธุรกิจบริการที่รับนัด: คลินิก สปา ร้านทำผม ยิม ร้านอาหาร
// MIT — KORP AI Automation (https://korpai.co)

/**
 * @param {number} bookingsPerMonth - จำนวนนัดต่อเดือน
 * @param {number} noShowRate - อัตรา no-show ปัจจุบัน (0..1) เช่น 0.28 = 28%
 * @param {number} profitPerBooking - กำไรเฉลี่ยต่อนัด (บาท)
 * @param {number} targetNoShowRate - อัตรา no-show เป้าหมายหลังทำระบบ (0..1)
 */
function noShowImpact(bookingsPerMonth, noShowRate, profitPerBooking, targetNoShowRate = 0.12) {
  const lostNow = bookingsPerMonth * noShowRate * profitPerBooking;
  const lostTarget = bookingsPerMonth * targetNoShowRate * profitPerBooking;
  const recovered = Math.max(0, lostNow - lostTarget);
  return {
    lostPerMonthNow: Math.round(lostNow),
    lostPerMonthTarget: Math.round(lostTarget),
    recoverablePerMonth: Math.round(recovered),
    recoverablePerYear: Math.round(recovered * 12),
  };
}

// ตัวอย่าง: คลินิก 300 นัด/เดือน, no-show 28%, กำไร 1,200 บ./นัด
console.log(noShowImpact(300, 0.28, 1200, 0.12));
// → { lostPerMonthNow: 100800, lostPerMonthTarget: 43200,
//     recoverablePerMonth: 57600, recoverablePerYear: 691200 }

export { noShowImpact };
