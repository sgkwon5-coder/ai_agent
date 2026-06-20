"""네이버 데이터랩 검색어 트렌드 API"""
import json
import sys
import urllib.request
import urllib.error

CLIENT_ID = "95ghhavekqPrpuRH1twC"
CLIENT_SECRET = "3tuU5LhiwE"
URL = "https://openapi.naver.com/v1/datalab/search"

VALID_TIME_UNITS = ("date", "week", "month")
VALID_DEVICES = ("pc", "mo")
VALID_GENDERS = ("m", "f")
VALID_AGES = [str(i) for i in range(1, 12)]
MIN_START_DATE = "2016-01-01"


def _validate(keyword_groups, start_date, device, gender, ages):
    if start_date < MIN_START_DATE:
        raise ValueError(f"startDate는 {MIN_START_DATE} 이후여야 합니다.")
    if len(keyword_groups) > 5:
        raise ValueError("keywordGroups는 최대 5개까지 설정할 수 있습니다.")
    for g in keyword_groups:
        if len(g.get("keywords", [])) > 20:
            raise ValueError(f"'{g.get('groupName')}' 그룹의 keywords는 최대 20개까지 설정할 수 있습니다.")
    if device and device not in VALID_DEVICES:
        raise ValueError(f"device는 {VALID_DEVICES} 중 하나여야 합니다.")
    if gender and gender not in VALID_GENDERS:
        raise ValueError(f"gender는 {VALID_GENDERS} 중 하나여야 합니다.")
    if ages:
        invalid = [a for a in ages if a not in VALID_AGES]
        if invalid:
            raise ValueError(f"ages에 유효하지 않은 값이 있습니다: {invalid}")


def search_trend(keyword_groups, start_date="2025-06-01", end_date="2026-06-20",
                 time_unit="month", device=None, gender=None, ages=None):
    _validate(keyword_groups, start_date, device, gender, ages)

    payload = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups,
    }
    if device:
        payload["device"] = device
    if gender:
        payload["gender"] = gender
    if ages:
        payload["ages"] = ages

    body = json.dumps(payload, ensure_ascii=False)

    request = urllib.request.Request(URL)
    request.add_header("X-Naver-Client-Id", CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
    request.add_header("Content-Type", "application/json")

    try:
        response = urllib.request.urlopen(request, data=body.encode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"[ERROR] HTTP {e.code}: {error_body}", file=sys.stderr)
        return e.code, {"error": error_body}

    code = response.getcode()
    result = json.loads(response.read().decode("utf-8"))
    return code, result


if __name__ == "__main__":
    keywords = [
        {"groupName": "AI", "keywords": ["인공지능", "AI"]},
        {"groupName": "ChatGPT", "keywords": ["챗GPT", "ChatGPT"]},
    ]

    print("=== 1. 기본 호출 (필수 파라미터만) ===")
    status, data = search_trend(keywords)
    print(f"HTTP Status: {status}")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    print("\n=== 2. 선택 파라미터 포함 (device=mo, gender=f, ages=3~5) ===")
    status, data = search_trend(
        keywords,
        start_date="2025-01-01",
        end_date="2026-06-20",
        time_unit="month",
        device="mo",
        gender="f",
        ages=["3", "4", "5"],
    )
    print(f"HTTP Status: {status}")
    print(json.dumps(data, indent=2, ensure_ascii=False))
