#!/usr/bin/env python3
"""
CSV → Supabase 자동 동기화 스크립트
GitHub Actions에서 CSV 변경 시 자동 실행됩니다.

사용법: python3 sync_csv.py
환경변수: SUPABASE_URL, SUPABASE_KEY
"""

import csv
import json
import os
import re
import sys
import urllib.request
import urllib.error

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://aehromyvzjzbkfcqspqi.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'sb_publishable_p_9upkexFkkMsjEA4yOKlg_Ssu_n4o3')

QA_CATEGORIES = {
    'Q1': 'EUV 펠리클', 'Q2': 'EUV 펠리클', 'Q3': '매출 전망',
    'Q4': '양산 역량', 'Q5': '경쟁사', 'Q6': '글로벌 전략',
    'Q7': 'EUV 펠리클', 'Q8': 'EUV 펠리클', 'Q9': '매출 전망',
    'Q10': 'EUV 펠리클', 'Q11': '기술', 'Q12': '기술',
    'Q13': '파트너십', 'Q14': '파트너십', 'Q15': '파트너십',
    'Q16': 'CNT 전선', 'Q17': 'CNT 전선', 'Q18': 'CNT 전선',
    'Q19': 'CNT 전선', 'Q20': 'CNT 전선', 'Q21': '기술',
    'Q22': 'CNT 전선', 'Q23': '투자 및 재무', 'Q24': '투자 및 재무',
    'Q25': 'IPO', 'Q26': '정리 사업', 'Q27': '정리 사업',
    'QX1': '정리 사업', 'QX2': '정리 사업'
}

def supabase_request(method, path, data=None):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, res.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')

def parse_answer(answer):
    """QA master answer를 summary/detail로 분리"""
    if not answer:
        return '', ''
    summary_match = re.search(r'\[요약\]\s*(.+?)(?=\[|$)', answer, re.DOTALL)
    summary = summary_match.group(1).strip().split('\n')[0].strip() if summary_match else ''
    detail_match = re.search(r'\[자세한 답변\](.*?)$', answer, re.DOTALL)
    if detail_match:
        detail = detail_match.group(1).strip()
        extras = re.findall(r'\[추가.*?\](.*?)(?=\[|$)', answer, re.DOTALL)
        for e in extras:
            detail += '\n\n' + e.strip()
    else:
        detail = answer.strip()
    return summary, detail

def read_csv(filepath):
    rows = []
    with open(filepath, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def sync():
    print("🔄 CSV → Supabase 동기화 시작...")

    # 1. 기존 데이터 전체 삭제
    status, body = supabase_request('DELETE', 'qa_items?id=gte.0')
    if status not in (200, 204):
        print(f"❌ 기존 데이터 삭제 실패: {status} {body}")
        sys.exit(1)
    print("✅ 기존 데이터 삭제 완료")

    items = []

    # 2. QA master CSV 읽기
    qa_path = 'data/qa_master.csv'
    if os.path.exists(qa_path):
        qa_rows = read_csv(qa_path)
        for i, row in enumerate(qa_rows):
            item_id = row.get('id', '').strip()
            answer = row.get('answer', '')
            summary, detail = parse_answer(answer)
            items.append({
                'tab': 'qa',
                'item_id': item_id,
                'category': QA_CATEGORIES.get(item_id, '기타'),
                'question': row.get('question', '').strip(),
                'summary': summary,
                'detail': detail,
                'keywords': row.get('keywords', '').strip(),
                'sort_order': i + 1
            })
        print(f"✅ QA master: {len(qa_rows)}개 로드")
    else:
        print(f"⚠️  {qa_path} 파일 없음, 건너뜀")

    # 3. FAQ CSV 읽기
    faq_path = 'data/interview_faq.csv'
    if os.path.exists(faq_path):
        faq_rows = read_csv(faq_path)
        for i, row in enumerate(faq_rows):
            items.append({
                'tab': 'faq',
                'item_id': row.get('id', '').strip(),
                'category': row.get('category', '').strip(),
                'question': row.get('question', '').strip(),
                'summary': row.get('answer_summary', '').strip(),
                'detail': row.get('answer_detailed', '').strip(),
                'keywords': row.get('keywords', '').strip(),
                'sort_order': i + 1
            })
        print(f"✅ FAQ: {len(faq_rows)}개 로드")
    else:
        print(f"⚠️  {faq_path} 파일 없음, 건너뜀")

    # 4. 새 데이터 삽입 (100개씩 배치)
    batch_size = 100
    total = 0
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        status, body = supabase_request('POST', 'qa_items', batch)
        if status not in (200, 201):
            print(f"❌ 삽입 실패: {status} {body}")
            sys.exit(1)
        total += len(batch)
        print(f"  → {total}/{len(items)}개 삽입 완료")

    print(f"\n🎉 동기화 완료! 총 {len(items)}개 항목이 DB에 업데이트되었습니다.")

if __name__ == '__main__':
    sync()
