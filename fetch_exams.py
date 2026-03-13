#!/usr/bin/env python3
"""
Lich Thi Duy Tan - Simple fetcher
Run: python fetch_exams.py
"""

import urllib.request
import urllib.parse
import re
import json

BASE_URL = 'https://pdaotao.duytan.edu.vn/EXAM_LIST/Default.aspx'

def fetch_page(page_num):
    import ssl
    url = f"{BASE_URL}?page={page_num}&lang=VN"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    # Create SSL context that doesn't verify certificates
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
        return response.read().decode('utf-8', errors='ignore')

def parse(html):
    exams = []
    # Find all IDs
    ids = re.findall(r'ID=(\d+)', html)

    for exam_id in ids:
        # Get context around ID
        pattern = rf'.{{0,300}}ID={exam_id}.{{0,600}}'
        match = re.search(pattern, html, re.DOTALL)
        if not match:
            continue

        text = re.sub(r'<[^>]+>', ' ', match.group(0))
        text = ' '.join(text.split())

        # Skip non-exam items
        skips = ['tuyen sinh', 'le phi', 'thi sinh', 'thong bao', 'tin tuc', 'huong dan', 'quy dinh']
        if any(s in text.lower() for s in skips):
            continue

        # Find course code
        code_match = re.search(r'\b([A-Z]{2,3}\s*\d{3,4})\b', text)
        if not code_match:
            continue

        ma_mon = code_match.group(1).strip()

        # Get name before code
        before = text[:code_match.start()]
        ten_mon = before.strip().split('\n')[-1].strip()[:80]

        # Get time
        time_match = re.search(r'(\d{1,2}:\d{2}\s+\d{1,2}/\d{1,2}/\d{2,4})', text)
        thoi_gian = time_match.group(1).strip() if time_match else ''

        # Get class
        class_match = re.search(rf'{re.escape(ma_mon)}\s*[-–—]?\s*([A-Z\-]+)', text)
        ma_lop = class_match.group(1).strip() if class_match else ''

        if ten_mon and len(ten_mon) > 2:
            exams.append({
                'id': exam_id,
                'tenMon': ten_mon,
                'maMon': ma_mon,
                'maLop': ma_lop,
                'thoiGian': thoi_gian
            })

    return exams

def main():
    all_exams = []
    print("Fetching exam data...")

    for page in range(1, 21):
        print(f"Page {page}/20...", end=" ")
        try:
            html = fetch_page(page)
            exams = parse(html)
            all_exams.extend(exams)
            print(f"{len(exams)} exams")
        except Exception as e:
            print(f"Error: {e}")

    # Remove duplicates
    seen = set()
    unique = []
    for e in all_exams:
        key = (e['maMon'], e['maLop'])
        if key not in seen:
            seen.add(key)
            unique.append(e)

    print(f"\nTotal: {len(unique)} exams")

    # Save to JSON
    with open('exams.json', 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    print("Saved to exams.json")

    # Print first few
    print("\nFirst 5 exams:")
    for e in unique[:5]:
        print(f"  {e['tenMon']} - {e['maMon']} ({e['maLop']}) - {e['thoiGian']}")

if __name__ == '__main__':
    main()
