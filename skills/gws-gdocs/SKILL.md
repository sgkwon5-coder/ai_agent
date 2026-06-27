---
name: gws-gdocs
description: >
  Google Docs 문서를 생성·작성·수정·조회·공유하는 스킬. gws CLI를 사용한다.
  사용자가 "구글 문서 만들어줘", "Google Docs에 작성", "docs 생성", "구글 독스",
  "문서 만들어", "보고서 구글 문서로", "회의록 docs에", "구글 doc에 정리해줘",
  "google doc 열어줘", "docs 링크", "문서 공유해줘", "구글 문서 수정" 같은 표현을
  사용하면 반드시 이 스킬을 사용한다. 내용을 구글 문서로 남기거나 공유하고 싶은
  맥락이라면 사용자가 명시적으로 "Google Docs"를 언급하지 않아도 이 스킬을 먼저 고려한다.
---

# Google Docs 스킬

`gws docs` CLI로 Google Docs 문서를 생성·작성·조회·수정한다.

## 인증 정보
- **계정**: sgkwon5@gmail.com
- **인증 확인**: `gws auth status`

---

## 1. 문서 생성

```powershell
# 빈 문서 생성 (제목만)
gws docs documents create --json '{"title":"문서 제목"}'
```

반환값에서 `documentId`를 추출해 이후 작업에 사용한다.

**문서 URL**: `https://docs.google.com/document/d/<documentId>/edit`

---

## 2. 텍스트 추가 (가장 빠른 방법)

```powershell
# 문서 끝에 텍스트 추가
gws docs +write --document <documentId> --text "추가할 내용"
```

- 줄바꿈: `\n` 사용
- 한국어 완전 지원
- 서식 없는 순수 텍스트만 가능

---

## 3. 서식 있는 콘텐츠 작성 (batchUpdate)

제목, 소제목, 표, 굵은 글씨 등 서식이 필요할 때는 `batchUpdate`를 사용한다.

### 기본 패턴

```powershell
gws docs documents batchUpdate `
  --params '{"documentId":"<DOC_ID>"}' `
  --json '{
    "requests": [
      {
        "insertText": {
          "location": {"index": 1},
          "text": "본문 내용\n"
        }
      }
    ]
  }'
```

### 주요 request 타입

| 목적 | request 타입 |
|------|-------------|
| 텍스트 삽입 | `insertText` |
| 단락 스타일 (제목/본문) | `updateParagraphStyle` |
| 텍스트 스타일 (굵게/기울임) | `updateTextStyle` |
| 표 삽입 | `insertTable` |
| 가로줄 | `insertPageBreak` |

### 단락 스타일 예시 (H1 제목)

```json
{
  "updateParagraphStyle": {
    "range": {"startIndex": 1, "endIndex": 10},
    "paragraphStyle": {"namedStyleType": "HEADING_1"},
    "fields": "namedStyleType"
  }
}
```

`namedStyleType` 값: `NORMAL_TEXT`, `HEADING_1` ~ `HEADING_6`, `TITLE`, `SUBTITLE`

### 굵은 글씨

```json
{
  "updateTextStyle": {
    "range": {"startIndex": 1, "endIndex": 10},
    "textStyle": {"bold": true},
    "fields": "bold"
  }
}
```

---

## 4. 문서 읽기

```powershell
# 문서 전체 내용 조회
gws docs documents get --params '{"documentId":"<DOC_ID>"}'
```

문서 URL에서 ID 추출: `https://docs.google.com/document/d/<DOC_ID>/edit`

---

## 5. 워크플로우 패턴

### 새 문서 생성 후 내용 작성 (추천 순서)

1. `documents create`로 문서 생성 → `documentId` 확보
2. `+write`로 빠르게 텍스트 추가 (서식 불필요 시)
   또는 `batchUpdate`로 서식 포함 내용 작성 (서식 필요 시)
3. 문서 URL을 사용자에게 전달

### Python 스크립트 활용 (복잡한 문서)

복잡한 서식, 반복 삽입, 표+텍스트 혼합이 필요한 경우:

```powershell
python "C:\Users\SBS\.claude\skills\gws-gdocs\scripts\gdocs_tool.py" create --title "제목"
python "C:\Users\SBS\.claude\skills\gws-gdocs\scripts\gdocs_tool.py" write --id <DOC_ID> --text "내용"
python "C:\Users\SBS\.claude\skills\gws-gdocs\scripts\gdocs_tool.py" read --id <DOC_ID>
```

---

## 6. Windows PowerShell JSON 주의사항

PowerShell에서 JSON에 한글이나 특수문자가 포함되면 `--json` 인수 대신 임시 파일을 활용한다:

```powershell
# 임시 JSON 파일 생성
$body = @{title="한글 제목"} | ConvertTo-Json
$body | Out-File -Encoding utf8 $env:TEMP\doc_body.json

# 파일 내용을 인수로 전달
gws docs documents create --json (Get-Content $env:TEMP\doc_body.json -Raw)
```

또는 Python 스크립트를 통해 처리한다.

---

## 7. 결과 전달 형식

작업 완료 후 사용자에게 반드시 다음을 포함하여 안내한다:

```
✅ Google Docs 문서 생성 완료
- 제목: [문서 제목]
- 링크: https://docs.google.com/document/d/<DOC_ID>/edit
- 내용: [간략 요약]
```
