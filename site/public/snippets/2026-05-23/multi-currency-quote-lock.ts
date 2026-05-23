// Multi-currency quote with 24h lock for Thai travel agencies
// Locks exchange rate at quote time; quote becomes invalid after window expires.
// Source: KORP AI — https://korpai.co/snippets/2026-05-23/multi-currency-quote-lock.ts
// License: MIT

export interface QuoteInput {
  basePriceTHB: number;
  currencies: ("USD" | "EUR" | "JPY" | "CNY" | "KRW")[];
  lockHours?: number; // default 24
}

export interface LockedQuote {
  base: { amount: number; currency: "THB" };
  converted: Record<string, number>;
  rateSnapshot: Record<string, number>;
  lockedAt: string;     // ISO8601
  validUntil: string;   // ISO8601
  validHoursRemaining: () => number;
  isExpired: () => boolean;
}

/**
 * Fetch live FX rates. In production this calls ExchangeRate-API / OpenExchangeRates.
 * Replace fetchRates with your provider; respond format here is THB-base.
 */
async function fetchRates(
  currencies: string[]
): Promise<Record<string, number>> {
  // STUB: replace with provider call. Rates are THB per 1 unit foreign.
  const stub: Record<string, number> = {
    USD: 36.05,
    EUR: 39.12,
    JPY: 0.226,
    CNY: 4.97,
    KRW: 0.0263,
  };
  const out: Record<string, number> = {};
  for (const c of currencies) {
    if (!stub[c]) throw new Error(`unsupported currency: ${c}`);
    out[c] = stub[c];
  }
  return out;
}

export async function buildLockedQuote(
  input: QuoteInput
): Promise<LockedQuote> {
  const lockHours = input.lockHours ?? 24;
  const rates = await fetchRates(input.currencies);
  const lockedAt = new Date();
  const validUntil = new Date(lockedAt.getTime() + lockHours * 3600_000);

  const converted: Record<string, number> = {};
  for (const c of input.currencies) {
    converted[c] = +(input.basePriceTHB / rates[c]).toFixed(2);
  }

  return {
    base: { amount: input.basePriceTHB, currency: "THB" },
    converted,
    rateSnapshot: rates,
    lockedAt: lockedAt.toISOString(),
    validUntil: validUntil.toISOString(),
    validHoursRemaining: () => {
      const ms = validUntil.getTime() - Date.now();
      return Math.max(0, +(ms / 3600_000).toFixed(2));
    },
    isExpired: () => Date.now() > validUntil.getTime(),
  };
}

// Example usage:
// const q = await buildLockedQuote({ basePriceTHB: 165000, currencies: ["USD","EUR","JPY"] });
// console.log(q);
