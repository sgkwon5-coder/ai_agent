"""회의록 자동 생성 스크립트 - Notion API"""
import sys
import io
import json
import requests
from datetime import date

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

NOTION_SECRET = "ntn_P5256324844awDeO3LHUGAqkb6vHro8Lx7PCETGXMKq16N"
DATABASE_ID = "7c11524bdf8149c3bf354c7c5a2c6c14"
BASE_URL = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_SECRET}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

MEETING_TEMPLATE = """## 안건

- [ ] 안건 1: {agenda_1}
- [ ] 안건 2: {agenda_2}
- [ ] 안건 3: {agenda_3}

---

## 논의 내용

| 안건 | 발언자 | 내용 |
|------|--------|------|
| 안건 1 | - | - |
| 안건 2 | - | - |
| 안건 3 | - | - |

---

## 결정 사항

1. (결정 1)
2. (결정 2)

---

## Action Items

| 항목 | 담당자 | 마감일 | 상태 |
|------|--------|--------|------|
| (할 일 1) | - | - | 대기 |
| (할 일 2) | - | - | 대기 |

---

## 다음 회의

- **일시**:
- **장소**:
- **사전 준비사항**:
"""


def create_meeting(title, meeting_date=None, meeting_type="정기회의", tags=None, agendas=None):
    """회의록 페이지를 Notion DB에 생성합니다."""
    if meeting_date is None:
        meeting_date = date.today().isoformat()
    if tags is None:
        tags = []
    if agendas is None:
        agendas = ["", "", ""]

    while len(agendas) < 3:
        agendas.append("")

    content = MEETING_TEMPLATE.format(
        agenda_1=agendas[0] or "(안건 입력)",
        agenda_2=agendas[1] or "(안건 입력)",
        agenda_3=agendas[2] or "(안건 입력)",
    )

    # Notion API 페이지 생성 payload
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "icon": {"type": "emoji", "emoji": "📋"},
        "properties": {
            "회의명": {"title": [{"text": {"content": title}}]},
            "날짜": {"date": {"start": meeting_date}},
            "상태": {"select": {"name": "예정"}},
            "유형": {"select": {"name": meeting_type}},
        },
        "children": markdown_to_blocks(content),
    }

    if tags:
        payload["properties"]["태그"] = {
            "multi_select": [{"name": t} for t in tags]
        }

    resp = requests.post(f"{BASE_URL}/pages", headers=HEADERS, json=payload)

    if resp.ok:
        data = resp.json()
        page_url = data.get("url", "")
        print(f"✅ 회의록 생성 완료!")
        print(f"   제목: {title}")
        print(f"   날짜: {meeting_date}")
        print(f"   유형: {meeting_type}")
        print(f"   URL: {page_url}")
        return data
    else:
        print(f"❌ 생성 실패: {resp.status_code}")
        print(f"   {resp.json()}")
        return None


def markdown_to_blocks(md_text):
    """간단한 마크다운을 Notion 블록으로 변환합니다."""
    blocks = []
    lines = md_text.strip().split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith("## "):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": line[3:]}}]}
            })
        elif line.startswith("---"):
            blocks.append({"object": "block", "type": "divider", "divider": {}})
        elif line.startswith("- [ ] "):
            blocks.append({
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": line[6:]}}],
                    "checked": False,
                }
            })
        elif line.startswith("- **"):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": parse_bold_text(line[2:])}
            })
        elif line.startswith("1. ") or line.startswith("2. ") or line.startswith("3. "):
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": line[3:]}}]}
            })
        elif line.startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|--"):
            # 테이블 처리
            table_rows = [line]
            i += 1  # separator
            i += 1
            while i < len(lines) and lines[i].startswith("|"):
                table_rows.append(lines[i])
                i += 1
            blocks.append(build_table(table_rows))
            continue
        elif line.strip() == "":
            pass
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": line}}]}
            })
        i += 1

    return blocks


def parse_bold_text(text):
    """**bold** 패턴을 rich_text 배열로 변환합니다."""
    parts = []
    while "**" in text:
        before, rest = text.split("**", 1)
        if "**" in rest:
            bold_text, text = rest.split("**", 1)
            if before:
                parts.append({"type": "text", "text": {"content": before}})
            parts.append({"type": "text", "text": {"content": bold_text}, "annotations": {"bold": True}})
        else:
            text = before + "**" + rest
            break
    if text:
        parts.append({"type": "text", "text": {"content": text}})
    return parts


def build_table(rows):
    """마크다운 테이블을 Notion table 블록으로 변환합니다."""
    parsed_rows = []
    for row in rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        parsed_rows.append(cells)

    width = len(parsed_rows[0]) if parsed_rows else 1

    table_rows = []
    for row_cells in parsed_rows:
        table_rows.append({
            "object": "block",
            "type": "table_row",
            "table_row": {
                "cells": [[{"type": "text", "text": {"content": cell}}] for cell in row_cells]
            }
        })

    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": width,
            "has_column_header": True,
            "has_row_header": False,
            "children": table_rows,
        }
    }


if __name__ == "__main__":
    print("\n📋 Notion 회의록 자동 생성\n")

    if len(sys.argv) > 1:
        title = sys.argv[1]
        meeting_date = sys.argv[2] if len(sys.argv) > 2 else None
        meeting_type = sys.argv[3] if len(sys.argv) > 3 else "정기회의"
        agendas = sys.argv[4:7] if len(sys.argv) > 4 else None
        create_meeting(title, meeting_date, meeting_type, agendas=agendas)
    else:
        print("사용법:")
        print('  python notion_meeting.py "회의 제목" [날짜] [유형] [안건1] [안건2] [안건3]')
        print("")
        print("예시:")
        print('  python notion_meeting.py "주간 팀 미팅" 2026-06-23 정기회의 "진행상황 공유" "이슈 논의" "다음주 계획"')
        print("")
        print("유형: 정기회의, 비정기, 1:1")
