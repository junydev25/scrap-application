import json

import requests
import yaml


def load_config(config_path):
    if not config_path or not config_path.exists():
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_data(data_path, filename):
    data_path.mkdir(parents=True, exist_ok=True)
    file_path = data_path / f"{filename}"
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)["data"]
            print("✅ 기존 데이터 로드")
            return data
        except Exception:
            print("⚠️ 기존 파일 읽기 실패, 새로 시작")
            return []
    else:
        print("✅ 새 데이터 생성")
        return []


def save(data, data_path, filename, total=1):
    data_path.mkdir(parents=True, exist_ok=True)
    with open(data_path / filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"✅ {total}개 JSON 파일로 저장", end="\n" if total > 1 else "\t")


def send_to_external_api(data, url):
    try:
        response = requests.post(url, json=data, timeout=30)  # 자동으로 JSON 변환
        if response.status_code == 200 or response.status_code == 201:
            resp_data = response.json()["message"]
            print(resp_data, end="")
        else:
            print("❌ 전송 실패")
    except requests.exceptions.RequestException as e:
        print(f"❌ API 요청 에러: {e}")


def convert_absolute_path(base_path, path):
    if not path.is_absolute():
        return base_path / path
    return path


def str2bool(value):
    if value == "true":
        return True
    elif value == "false":
        return False
    return None


def search_not_none(*values):
    for value in values:
        if value is not None:
            return value
    return False
