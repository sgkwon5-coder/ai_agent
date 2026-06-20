"""네이버 데이터랩 쇼핑 인사이트 API"""
import json
import sys
import urllib.request
import urllib.error

CLIENT_ID = "95ghhavekqPrpuRH1twC"
CLIENT_SECRET = "3tuU5LhiwE"
URL = "https://openapi.naver.com/v1/datalab/shopping/categories"

VALID_TIME_UNITS = ("date", "week", "month")
VALID_DEVICES = ("pc", "mo")
VALID_GENDERS = ("m", "f")
VALID_AGES = ["10", "20", "30", "40", "50", "60"]
MIN_START_DATE = "2016-01-01"


def _validate(categories, start_date, device, gender, ages):
    if start_date < MIN_START_DATE:
        raise ValueError(f"startDate는 {MIN_START_DATE} 이후여야 합니다.")
    if len(categories) > 3:
        raise ValueError("category는 최대 3개까지 설정할 수 있습니다.")
    if device and device not in VALID_DEVICES:
        raise ValueError(f"device는 {VALID_DEVICES} 중 하나여야 합니다.")
    if gender and gender not in VALID_GENDERS:
        raise ValueError(f"gender는 {VALID_GENDERS} 중 하나여야 합니다.")
    if ages:
        invalid = [a for a in ages if a not in VALID_AGES]
        if invalid:
            raise ValueError(f"ages에 유효하지 않은 값이 있습니다: {invalid}")


def shopping_insight(categories, start_date="2025-06-01", end_date="2026-06-20",
                     time_unit="month", device=None, gender=None, ages=None):
    _validate(categories, start_date, device, gender, ages)

    payload = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "category": categories,
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
    cats = [
        {"name": "패션의류", "param": ["50000000"]},
        {"name": "디지털/가전", "param": ["50000003"]},
    ]

    print("=== 1. 기본 호출 (필수 파라미터만) ===")
    status, data = shopping_insight(cats)
    print(f"HTTP Status: {status}")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    print("\n=== 2. 선택 파라미터 포함 (device=mo, gender=m, ages=20~40대) ===")
    status, data = shopping_insight(
        cats,
        start_date="2025-01-01",
        end_date="2026-06-20",
        time_unit="month",
        device="mo",
        gender="m",
        ages=["20", "30", "40"],
    )
    print(f"HTTP Status: {status}")
    print(json.dumps(data, indent=2, ensure_ascii=False))
