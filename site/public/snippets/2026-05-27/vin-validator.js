/**
 * VIN (Vehicle Identification Number) validator + decoder
 * Used in KORP AI's car dealer chatbot guardrail to catch รถสวมทะเบียน
 * before listing for sale.
 *
 * Validates ISO 3779 (post-1981) 17-character VINs:
 *   - Length = 17
 *   - No I, O, Q (anti-ambiguity)
 *   - Check-digit (position 9) using ISO 3779 weights
 * Decodes WMI (world manufacturer identifier, 3 chars)
 * and approximate model year (position 10).
 *
 * Usage:
 *   validateVin("1HGCM82633A123456") // => { valid: true, wmi: "1HG", year: 2003|2033 }
 */

const WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2];
const TRANSLIT = {
  A: 1, B: 2, C: 3, D: 4, E: 5, F: 6, G: 7, H: 8,
  J: 1, K: 2, L: 3, M: 4, N: 5, P: 7, R: 9,
  S: 2, T: 3, U: 4, V: 5, W: 6, X: 7, Y: 8, Z: 9,
};
const YEAR_TABLE = {
  A: [1980, 2010], B: [1981, 2011], C: [1982, 2012], D: [1983, 2013],
  E: [1984, 2014], F: [1985, 2015], G: [1986, 2016], H: [1987, 2017],
  J: [1988, 2018], K: [1989, 2019], L: [1990, 2020], M: [1991, 2021],
  N: [1992, 2022], P: [1993, 2023], R: [1994, 2024], S: [1995, 2025],
  T: [1996, 2026], V: [1997, 2027], W: [1998, 2028], X: [1999, 2029],
  Y: [2000, 2030], 1: [2001, 2031], 2: [2002, 2032], 3: [2003, 2033],
  4: [2004, 2034], 5: [2005, 2035], 6: [2006, 2036], 7: [2007, 2037],
  8: [2008, 2038], 9: [2009, 2039],
};

export function validateVin(vin) {
  if (typeof vin !== "string") return { valid: false, error: "VIN must be string" };
  vin = vin.toUpperCase().trim();
  if (vin.length !== 17) return { valid: false, error: `Length ${vin.length}, expected 17` };
  if (/[IOQ]/.test(vin)) return { valid: false, error: "Contains forbidden I/O/Q" };
  if (!/^[A-HJ-NPR-Z0-9]{17}$/.test(vin)) return { valid: false, error: "Invalid characters" };

  // ISO 3779 check digit
  let sum = 0;
  for (let i = 0; i < 17; i++) {
    const c = vin[i];
    const val = /[0-9]/.test(c) ? Number(c) : TRANSLIT[c];
    if (val === undefined) return { valid: false, error: `Cannot translit ${c}` };
    sum += val * WEIGHTS[i];
  }
  const expected = sum % 11;
  const expectedChar = expected === 10 ? "X" : String(expected);
  if (vin[8] !== expectedChar) {
    return { valid: false, error: `Check digit mismatch: got ${vin[8]}, expected ${expectedChar}` };
  }
  return {
    valid: true,
    wmi: vin.slice(0, 3),
    vds: vin.slice(3, 9),
    vis: vin.slice(9),
    year: YEAR_TABLE[vin[9]] || null,
  };
}

// Demo
if (typeof require !== "undefined" && require.main === module) {
  for (const v of ["1HGCM82633A123456", "JH4DA9450MS016526", "INVALIDVIN12345A1"]) {
    console.log(v, "=>", validateVin(v));
  }
}
