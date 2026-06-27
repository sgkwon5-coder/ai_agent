"""
gdocs_tool.py - Google Docs helper via gws CLI
사용법:
  python gdocs_tool.py create --title "문서 제목"
  python gdocs_tool.py write --id <DOC_ID> --text "내용"
  python gdocs_tool.py read --id <DOC_ID>
  python gdocs_tool.py url --id <DOC_ID>
"""

import argparse
import json
import subprocess
import sys
import tempfile
import os


def run_gws(args: list[str]) -> dict:
    result = subprocess.run(
        ["gws"] + args,
        capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        print(f"[ERROR] {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout) if result.stdout.strip() else {}


def create_doc(title: str) -> str:
    body = json.dumps({"title": title}, ensure_ascii=False)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        f.write(body)
        tmp = f.name
    try:
        result = subprocess.run(
            ["gws", "docs", "documents", "create", "--json", open(tmp, encoding="utf-8").read()],
            capture_output=True, text=True, encoding="utf-8"
        )
        if result.returncode != 0:
            print(f"[ERROR] {result.stderr}", file=sys.stderr)
            sys.exit(1)
        data = json.loads(result.stdout)
        doc_id = data.get("documentId", "")
        print(f"documentId: {doc_id}")
        print(f"URL: https://docs.google.com/document/d/{doc_id}/edit")
        return doc_id
    finally:
        os.unlink(tmp)


def write_doc(doc_id: str, text: str) -> None:
    result = subprocess.run(
        ["gws", "docs", "+write", "--document", doc_id, "--text", text],
        capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        print(f"[ERROR] {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print("텍스트 추가 완료")


def read_doc(doc_id: str) -> None:
    result = subprocess.run(
        ["gws", "docs", "documents", "get",
         "--params", json.dumps({"documentId": doc_id})],
        capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        print(f"[ERROR] {result.stderr}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(result.stdout)
    title = data.get("title", "")
    print(f"제목: {title}")
    print(f"URL: https://docs.google.com/document/d/{doc_id}/edit")
    # 본문 텍스트 추출
    body = data.get("body", {}).get("content", [])
    texts = []
    for element in body:
        for para_elem in element.get("paragraph", {}).get("elements", []):
            t = para_elem.get("textRun", {}).get("content", "")
            if t.strip():
                texts.append(t)
    print("\n--- 본문 ---")
    print("".join(texts))


def main():
    parser = argparse.ArgumentParser(description="Google Docs helper")
    sub = parser.add_subparsers(dest="cmd")

    p_create = sub.add_parser("create", help="새 문서 생성")
    p_create.add_argument("--title", required=True, help="문서 제목")

    p_write = sub.add_parser("write", help="텍스트 추가")
    p_write.add_argument("--id", required=True, help="Document ID")
    p_write.add_argument("--text", required=True, help="추가할 텍스트")

    p_read = sub.add_parser("read", help="문서 읽기")
    p_read.add_argument("--id", required=True, help="Document ID")

    p_url = sub.add_parser("url", help="문서 URL 출력")
    p_url.add_argument("--id", required=True, help="Document ID")

    args = parser.parse_args()

    if args.cmd == "create":
        create_doc(args.title)
    elif args.cmd == "write":
        write_doc(args.id, args.text)
    elif args.cmd == "read":
        read_doc(args.id)
    elif args.cmd == "url":
        print(f"https://docs.google.com/document/d/{args.id}/edit")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
