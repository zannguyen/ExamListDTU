#!/usr/bin/env python3
"""
Simple HTTP server - auto fetches data from Duy Tan website
"""

import http.server
import socketserver
import json
import os
import urllib.request
import re
import ssl

PORT = int(os.environ.get("PORT", 8888))
BASE_URL = 'https://pdaotao.duytan.edu.vn/EXAM_LIST/Default.aspx'

def fetch_from_web():
    """Fetch exam data from university website"""
    print("Fetching latest exam data from web...")
    all_exams = []

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    for page in range(1, 21):
        print(f"Page {page}/20...", end=" ", flush=True)
        try:
            url = f"{BASE_URL}?page={page}&lang=VN"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
                html = response.read().decode('utf-8', errors='ignore')

            # Parse exams from HTML - extract raw text for each exam
            ids = re.findall(r'ID=(\d+)', html)
            for exam_id in ids:
                pattern = rf'.{{0,300}}ID={exam_id}.{{0,600}}'
                match = re.search(pattern, html, re.DOTALL)
                if not match:
                    continue

                text = re.sub(r'<[^>]+>', ' ', match.group(0))
                text = ' '.join(text.split())

                # Store raw text - keep everything for search (no filtering)
                if len(text) > 5:
                    all_exams.append({
                        'id': exam_id,
                        'text': text
                    })

            print(f"done")
        except Exception as e:
            print(f"Error: {e}")

    # Remove duplicates
    seen = set()
    unique = []
    for e in all_exams:
        # Use ID as key to avoid duplicates
        key = e['id']
        if key not in seen:
            seen.add(key)
            unique.append(e)

    print(f"Total: {len(unique)} exams")
    return unique

# Always fetch fresh from web on startup
print("Loading exam data from web...")
exams_data = fetch_from_web()

# HTML Template
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tra cứu Lịch Thi Duy Tân</title>
    <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --primary: #00f0ff;
            --secondary: #ff00aa;
            --accent: #8b5cf6;
            --dark: #0a0a0f;
            --darker: #050508;
            --card-bg: #12121a;
            --text: #e0e0e0;
            --text-muted: #888;
        }
        body {
            font-family: 'Be Vietnam Pro', sans-serif;
            background: var(--darker);
            min-height: 100vh;
            color: var(--text);
            background-image:
                radial-gradient(ellipse at top, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
                radial-gradient(ellipse at bottom right, rgba(255, 0, 170, 0.1) 0%, transparent 50%),
                linear-gradient(180deg, var(--darker) 0%, var(--dark) 100%);
        }
        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            pointer-events: none;
            z-index: 0;
        }
        .container { max-width: 1100px; margin: 0 auto; position: relative; z-index: 1; padding: 20px; }
        .header { text-align: center; padding: 40px 0 30px; }
        .header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 200px;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--primary), transparent);
        }
        .logo {
            font-family: 'Be Vietnam Pro', sans-serif;
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: 2px;
            margin-bottom: 10px;
        }
        .tagline { font-size: 1rem; color: var(--text-muted); letter-spacing: 2px; }
        .search-box {
            background: var(--card-bg);
            border: 1px solid rgba(0, 240, 255, 0.2);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            position: relative;
        }
        .search-box::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 1px;
            background: linear-gradient(90deg, transparent, var(--primary), transparent);
        }
        .search-inputs { display: flex; gap: 15px; flex-wrap: wrap; align-items: flex-end; }
        .input-group { flex: 1; min-width: 220px; }
        .input-group label {
            display: block;
            margin-bottom: 10px;
            color: var(--primary);
            font-weight: 600;
            font-size: 0.95rem;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .input-group input {
            width: 100%;
            padding: 14px 18px;
            background: var(--darker);
            border: 1px solid rgba(0, 240, 255, 0.3);
            border-radius: 8px;
            font-size: 1rem;
            color: var(--text);
            font-family: 'Be Vietnam Pro', sans-serif;
            transition: all 0.3s;
        }
        .input-group input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
        }
        .btn-group { display: flex; gap: 12px; }
        .btn {
            padding: 14px 28px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
            font-family: 'Be Vietnam Pro', sans-serif;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--accent));
            color: var(--dark);
        }
        .btn-primary:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(0, 240, 255, 0.4); }
        .btn-secondary {
            background: transparent;
            border: 1px solid var(--secondary);
            color: var(--secondary);
        }
        .btn-secondary:hover { background: var(--secondary); color: white; }
        .stats { display: flex; gap: 30px; margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); }
        .stat-item { color: var(--text-muted); font-size: 0.95rem; }
        .stat-item strong { color: var(--primary); font-weight: 700; }
        .results {
            background: var(--card-bg);
            border: 1px solid rgba(0, 240, 255, 0.2);
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            position: relative;
        }
        .results::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 1px;
            background: linear-gradient(90deg, transparent, var(--secondary), transparent);
        }
        .results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .results-header h2 { font-size: 1.3rem; color: var(--text); letter-spacing: 2px; }
        .results-count { background: linear-gradient(135deg, var(--secondary), var(--accent)); color: white; padding: 6px 16px; border-radius: 20px; font-size: 0.9rem; font-weight: 600; }
        .exam-list { list-style: none; max-height: 550px; overflow-y: auto; }
        .exam-list::-webkit-scrollbar { width: 6px; }
        .exam-list::-webkit-scrollbar-track { background: var(--darker); }
        .exam-list::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 3px; }
        .exam-item {
            padding: 20px;
            background: var(--darker);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 12px;
            margin-bottom: 12px;
            transition: all 0.3s;
        }
        .exam-item:hover {
            border-color: var(--primary);
            transform: translateX(8px);
            box-shadow: 0 5px 25px rgba(0, 240, 255, 0.15);
        }
        .exam-item .subject { font-weight: 700; color: white; font-size: 1.1rem; margin-bottom: 8px; }
        .exam-item .code { color: var(--primary); font-weight: 600; font-size: 1rem; }
        .exam-item .time { color: var(--secondary); font-size: 0.95rem; margin-top: 8px; }
        .exam-item .detail-link {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-top: 15px;
            padding: 10px 20px;
            background: linear-gradient(135deg, var(--accent), var(--primary));
            color: white;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 600;
            border-radius: 6px;
            transition: all 0.3s;
        }
        .exam-item .detail-link:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(139, 92, 246, 0.5); }
        .no-results { text-align: center; padding: 50px; color: var(--text-muted); }
        .footer { text-align: center; padding: 30px; color: var(--text-muted); font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1 class="logo">LỊCH THI DUY TÂN</h1>
            <p class="tagline">Tra cuu nhanh chong - Tim kiem thong minh</p>
        </header>

        <div class="search-box">
            <div class="search-inputs">
                <div class="input-group">
                    <label for="maMon">Tim kiem</label>
                    <input type="text" id="maMon" placeholder="Nhap ma mon, ten mon, lop...">
                </div>
                <div class="btn-group">
                    <button class="btn btn-primary" onclick="refreshData()">Tai lai</button>
                    <button class="btn btn-secondary" onclick="showAll()">Tat ca</button>
                </div>
            </div>
            <div class="stats">
                <div class="stat-item">TONG: <strong id="total-count">0</strong></div>
            </div>
        </div>

        <div class="results">
            <div class="results-header">
                <h2>KET QUA</h2>
                <span class="results-count" id="results-count">0</span>
            </div>
            <ul class="exam-list" id="exam-list">
                <li class="no-results">Dang tai...</li>
            </ul>
        </div>

        <footer class="footer">
            <p>© 2026 Duy Tan Exam Finder</p>
        </footer>
    </div>

    <script>
        let allExams = EXAMS_DATA;

        function refreshData() {
            window.location.href = '/refresh';
        }

        function init() {
            document.getElementById('total-count').textContent = allExams.length;
            showAll();
        }

        function showAll() {
            displayResults(allExams);
            document.getElementById('maMon').value = '';
        }

        function filterExams() {
            const searchInput = document.getElementById('maMon').value.toLowerCase().trim();

            let filtered = allExams;
            if (searchInput) {
                filtered = filtered.filter(exam =>
                    exam.text.toLowerCase().includes(searchInput)
                );
            }
            displayResults(filtered);
        }

        function displayResults(exams) {
            const examList = document.getElementById('exam-list');
            const resultsCount = document.getElementById('results-count');
            resultsCount.textContent = exams.length;

            if (exams.length === 0) {
                examList.innerHTML = '<li class="no-results">Khong tim thay ket qua</li>';
                return;
            }

            examList.innerHTML = exams.map(exam => `
                <li class="exam-item">
                    <div class="subject">${exam.text || exam.tenMon || ''} ${exam.maMon || ''} ${exam.maLop || ''} (${exam.thoiGian || ''})</div>
                    <a class="detail-link" href="https://pdaotao.duytan.edu.vn/EXAM_LIST_Detail/?ID=${exam.id}&lang=VN" target="_blank">
                        Tai file Excel
                    </a>
                </li>
            `).join('');
        }

        document.getElementById('maMon').addEventListener('input', filterExams);
        window.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>
'''.replace('EXAMS_DATA', json.dumps(exams_data))

class ExamHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        elif self.path == '/refresh':
            # Return loading message immediately (don't fetch in request)
            # User can manually refresh later
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            msg = '''<!DOCTYPE html><html><head><meta charset="UTF-8">
            <script>setTimeout(()=>window.location='/',2000)</script>
            </head><body style="background:#050508;color:#00f0ff;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;">
            <h1>Dang tai lai du lieu...</h1></body></html>'''
            self.wfile.write(msg.encode('utf-8'))
        else:
            self.send_error(404)

if __name__ == '__main__':
    print("=" * 50)
    print("Starting Lich Thi Duy Tan Server")
    print("=" * 50)
    print(f"Open browser: http://localhost:{PORT}")
    print("=" * 50)

    with socketserver.TCPServer(("", PORT), ExamHandler) as httpd:
        httpd.serve_forever()
