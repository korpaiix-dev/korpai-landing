#!/usr/bin/env python3
"""thai_chunker.py — Thai-aware text chunker for RAG (no dependencies).

Thai has no spaces between words, so naive fixed-size chunkers cut mid-sentence
and wreck retrieval. This chunker:
  1. splits on markdown headings + blank lines first (structure > size)
  2. then packs paragraphs into chunks of ~target chars (default 800 ≈ 250-400 Thai tokens)
  3. only splits inside a paragraph at Thai sentence-ish boundaries
     (space after ครับ/ค่ะ/นะคะ/ฯลฯ, ".", "!", "?", newline) — never mid-word
  4. adds overlap so context survives the cut

Usage: python3 thai_chunker.py doc.md            # prints one chunk per --- line
       python3 thai_chunker.py doc.md --jsonl    # JSONL with id/text/heading
Companion to: https://korpai.co/blog/knowledge-base-ai-chatbot-เตรียมข้อมูล-sme-ไทย-2026
MIT license — KORP AI (korpai.co)
"""
import json, re, sys

TARGET, OVERLAP = 800, 120
SENT_END = re.compile(r"(?<=[\.\!\?])\s+|(?<=ครับ)\s+|(?<=ค่ะ)\s+|(?<=คะ)\s+|(?<=นะ)\s+|(?<=แล้ว)\s+|\n+")

def split_sentences(par: str):
    parts = [p.strip() for p in SENT_END.split(par) if p and p.strip()]
    return parts or [par.strip()]

def chunk(text: str):
    blocks, heading, chunks = [], "", []
    for raw in re.split(r"\n{2,}", text):
        b = raw.strip()
        if not b: continue
        if b.startswith("#"):
            heading = b.lstrip("# ").strip(); continue
        blocks.append((heading, b))
    buf, buf_head = "", ""
    for head, b in blocks:
        if buf and (len(buf) + len(b) > TARGET or head != buf_head):
            chunks.append((buf_head, buf.strip())); buf = buf[-OVERLAP:] if head == buf_head else ""
        buf_head = head
        if len(b) <= TARGET:
            buf += ("\n" if buf else "") + b
        else:  # oversized paragraph → sentence-pack
            for s in split_sentences(b):
                if len(buf) + len(s) > TARGET and buf:
                    chunks.append((buf_head, buf.strip())); buf = buf[-OVERLAP:]
                buf += (" " if buf else "") + s
    if buf.strip(): chunks.append((buf_head, buf.strip()))
    return chunks

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit("usage: thai_chunker.py doc.md [--jsonl]")
    text = open(sys.argv[1], encoding="utf-8").read()
    out = chunk(text)
    for i, (head, c) in enumerate(out):
        if "--jsonl" in sys.argv:
            print(json.dumps({"id": f"chunk-{i}", "heading": head, "text": c}, ensure_ascii=False))
        else:
            print(f"--- chunk {i} [{head}] ({len(c)} chars)\n{c}\n")
    print(f"[done] {len(out)} chunks, avg {sum(len(c) for _, c in out)//max(len(out),1)} chars", file=sys.stderr)
