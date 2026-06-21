"""Notion API 접근 테스트 스크립트"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests

NOTION_SECRET = "ntn_P5256324844awDeO3LHUGAqkb6vHro8Lx7PCETGXMKq16N"
BASE_URL = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_SECRET}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def test_get_me():
    """봇 사용자 정보 조회 (GET /v1/users/me)"""
    print("=" * 50)
    print("[1] 봇 사용자 정보 조회")
    print("=" * 50)
    resp = requests.get(f"{BASE_URL}/users/me", headers=HEADERS)
    print(f"Status: {resp.status_code}")
    if resp.ok:
        data = resp.json()
        print(f"  Bot Name: {data.get('name')}")
        print(f"  Type: {data.get('type')}")
        print(f"  ID: {data.get('id')}")
    else:
        print(f"  Error: {resp.json()}")
    print()
    return resp.ok


def test_search():
    """접근 가능한 페이지/DB 검색 (POST /v1/search)"""
    print("=" * 50)
    print("[2] 접근 가능한 페이지/데이터베이스 검색")
    print("=" * 50)
    payload = {"page_size": 10}
    resp = requests.post(f"{BASE_URL}/search", headers=HEADERS, json=payload)
    print(f"Status: {resp.status_code}")
    if resp.ok:
        data = resp.json()
        results = data.get("results", [])
        print(f"  검색 결과 수: {len(results)}")
        for i, item in enumerate(results, 1):
            obj_type = item.get("object")
            title = ""
            if obj_type == "page":
                props = item.get("properties", {})
                title_prop = props.get("title") or props.get("Name") or props.get("이름")
                if title_prop and title_prop.get("title"):
                    title = "".join(t.get("plain_text", "") for t in title_prop["title"])
            elif obj_type == "database":
                title_list = item.get("title", [])
                title = "".join(t.get("plain_text", "") for t in title_list)
            print(f"  [{i}] {obj_type}: {title or '(제목 없음)'} | ID: {item['id']}")
        if not results:
            print("  ⚠ 결과 없음 — Integration에 페이지를 공유해야 접근 가능합니다.")
    else:
        print(f"  Error: {resp.json()}")
    print()
    return resp.ok


def test_list_users():
    """워크스페이스 사용자 목록 조회 (GET /v1/users)"""
    print("=" * 50)
    print("[3] 워크스페이스 사용자 목록")
    print("=" * 50)
    resp = requests.get(f"{BASE_URL}/users", headers=HEADERS)
    print(f"Status: {resp.status_code}")
    if resp.ok:
        data = resp.json()
        for user in data.get("results", []):
            print(f"  - {user.get('name')} ({user.get('type')}) | {user.get('id')}")
    else:
        print(f"  Error: {resp.json()}")
    print()
    return resp.ok


if __name__ == "__main__":
    print("\n🔑 Notion API 접근 테스트 시작\n")
    results = {
        "봇 정보 조회": test_get_me(),
        "페이지 검색": test_search(),
        "사용자 목록": test_list_users(),
    }
    print("=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    for name, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"  {name}: {status}")
