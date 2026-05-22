"""
parts-catalog-rag.py
KORP AI — RAG query over auto-parts catalog with multi-brand namespacing.
Prevents AI hallucination by enforcing namespace lookup (Honda parts cannot leak into Toyota query).
"""

from dataclasses import dataclass

@dataclass
class PartQuery:
    brand: str          # Honda, Toyota, Mazda, BYD, Tesla
    model: str          # Civic FC, Corolla, CX-5, Atto3
    year: int
    part_category: str  # brake_pads, oil_filter, tires, battery

# In production: replace with Qdrant / Pinecone vector search
# This is a stub showing the multi-brand isolation pattern
CATALOG = {
    'Honda::Civic FC::2018::brake_pads': [
        {'sku': 'AKB-CFC-F',  'brand': 'Akebono OE',  'price': 1850, 'labor': 350, 'minutes': 45},
        {'sku': 'BND-CFC-F',  'brand': 'Bendix CT',   'price': 1250, 'labor': 350, 'minutes': 45},
        {'sku': 'BRB-CFC-F',  'brand': 'Brembo Sport','price': 3400, 'labor': 350, 'minutes': 45},
    ],
    'Toyota::Corolla::2020::brake_pads': [
        {'sku': 'TYT-COR-F',  'brand': 'Toyota OE',   'price': 1650, 'labor': 350, 'minutes': 40},
    ],
}

def lookup_parts(q: PartQuery) -> list[dict]:
    """Namespaced lookup — refuses cross-brand fallback."""
    key = f'{q.brand}::{q.model}::{q.year}::{q.part_category}'
    return CATALOG.get(key, [])

def format_quote_thai(q: PartQuery, results: list[dict]) -> str:
    if not results:
        return (
            f"ขออภัยครับ ไม่พบ {q.part_category.replace('_',' ')} "
            f"สำหรับ {q.brand} {q.model} {q.year} ในสต็อก\n"
            f"ส่งให้ช่างเช็คให้ภายใน 30 นาทีนะครับ"
        )
    label = {
        'brake_pads': 'ผ้าเบรก',
        'oil_filter': 'กรองน้ำมันเครื่อง',
        'tires': 'ยาง',
        'battery': 'แบตเตอรี่',
    }.get(q.part_category, q.part_category)
    lines = [f"{label}สำหรับ {q.brand} {q.model} {q.year} ที่ร้านมี {len(results)} ระดับครับ:"]
    for r in results:
        lines.append(f"- {r['brand']}: {r['price']:,} บาท/ชุด · ค่าแรง {r['labor']} บาท · ใช้เวลา {r['minutes']} นาที")
    lines.append('\nอยากจองคิวเลยไหมครับ?')
    return '\n'.join(lines)

if __name__ == '__main__':
    q = PartQuery(brand='Honda', model='Civic FC', year=2018, part_category='brake_pads')
    print(format_quote_thai(q, lookup_parts(q)))
