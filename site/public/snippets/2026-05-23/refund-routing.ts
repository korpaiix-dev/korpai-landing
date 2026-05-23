// Refund routing decision tree for Thai outbound travel agencies.
// IATA / non-IATA / hotel-direct / OTA each have different refund windows
// and intermediary roles. This module decides which workflow to enqueue.
// Source: KORP AI - https://korpai.co/snippets/2026-05-23/refund-routing.ts
// License: MIT

export type Channel = "IATA_airline" | "non_IATA_airline" | "hotel_direct" | "OTA" | "agency_package";

export interface RefundCase {
  channel: Channel;
  bookingDate: string;        // ISO
  departureDate: string;      // ISO
  paidAmountTHB: number;
  reason: "customer_cancel" | "airline_cancel" | "force_majeure" | "agency_error";
  insuranceCovers?: boolean;
}

export interface RefundDecision {
  primaryHandler: "airline_direct" | "ota_portal" | "agency_ops" | "insurer";
  estimatedDays: number;
  refundableTHB: number;
  notes: string[];
}

export function routeRefund(c: RefundCase): RefundDecision {
  const daysToDeparture = Math.max(
    0,
    Math.ceil((+new Date(c.departureDate) - Date.now()) / 86400000)
  );
  const notes: string[] = [];

  // Force majeure or airline cancel: airline / IATA settlement first
  if (c.reason === "airline_cancel" || c.reason === "force_majeure") {
    notes.push("Initiate IATA BSP refund or chargeback per IATA Resolution 824r.");
    return {
      primaryHandler: c.channel === "IATA_airline" ? "airline_direct" : "agency_ops",
      estimatedDays: 14,
      refundableTHB: c.paidAmountTHB,
      notes,
    };
  }

  // Customer cancel - depends on channel
  switch (c.channel) {
    case "IATA_airline": {
      // Approx fare-rule window; real rule comes from PNR
      const refundPct = daysToDeparture >= 30 ? 0.85 : daysToDeparture >= 7 ? 0.5 : 0.0;
      return {
        primaryHandler: "airline_direct",
        estimatedDays: 7,
        refundableTHB: Math.floor(c.paidAmountTHB * refundPct),
        notes: [...notes, `Fare-rule window: ${daysToDeparture} days to departure -> ${Math.round(refundPct*100)}% refundable`],
      };
    }
    case "non_IATA_airline":
      return {
        primaryHandler: "agency_ops",
        estimatedDays: 21,
        refundableTHB: Math.floor(c.paidAmountTHB * 0.4),
        notes: [...notes, "Non-IATA: refund goes via wholesaler, longer SLA."],
      };
    case "hotel_direct": {
      const refundPct = daysToDeparture >= 14 ? 1.0 : daysToDeparture >= 3 ? 0.5 : 0.0;
      return {
        primaryHandler: "agency_ops",
        estimatedDays: 5,
        refundableTHB: Math.floor(c.paidAmountTHB * refundPct),
        notes: [...notes, "Hotel free-cancel window checked."],
      };
    }
    case "OTA":
      return {
        primaryHandler: "ota_portal",
        estimatedDays: 10,
        refundableTHB: Math.floor(c.paidAmountTHB * (daysToDeparture >= 7 ? 0.8 : 0)),
        notes: [...notes, "Submit through OTA partner portal; cannot bypass."],
      };
    case "agency_package": {
      const base = daysToDeparture >= 45 ? 0.85
                 : daysToDeparture >= 21 ? 0.5
                 : daysToDeparture >= 7  ? 0.25 : 0;
      const insured = c.insuranceCovers ? "; travel insurance may cover gap" : "";
      return {
        primaryHandler: c.insuranceCovers ? "insurer" : "agency_ops",
        estimatedDays: 14,
        refundableTHB: Math.floor(c.paidAmountTHB * base),
        notes: [...notes, `Package T&C tier: ${daysToDeparture}d -> ${Math.round(base*100)}%${insured}`],
      };
    }
  }
}

// Quick smoke test
if (typeof require !== "undefined" && require.main === module) {
  const out = routeRefund({
    channel: "IATA_airline",
    bookingDate: "2026-05-01",
    departureDate: "2026-08-10",
    paidAmountTHB: 165000,
    reason: "customer_cancel",
  });
  console.log(out);
}
