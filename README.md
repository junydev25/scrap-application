# Scrap Application

## Description
해당 Scraping은 Playwright를 사용 하므로 Selenium과 다르게 브라우저에 종속적이지도 않고 설치도 매우 쉽습니다.
```markdown
OS: Ubuntu 24.04.1 LTS
Playwright: 1.55.0
Python*: 3.10.18
```

---

Scraping을 할 때 기준 HTML은 `http://localhost:8000`으로 했으나 HTML마다 달라질 수 있습니다. 현재 CSS Selector는 다음과 같이 구성되어 있습니다.
- 로그인
  - ID 또는 Username: `input[type='text'][name='username'][id='id_username']`
  - Password: `input[type='password']`
> [!NOTE]
> Password를 찾는 것은 명확할 수 있지만 ID를 찾는 것은 명확하지 않을 수 있습니다. 
> 따라서 만약 로그인 페이지에 input이 두 곳 밖에 없다면 Password를 찾고 나머지 하나를 ID라고 단정지을 수 있습니다.
- 리스트 요소들
  - 현재 보이는 HTML에 존재하는 리스트 요소들: `ul a`
  - 리스트 요소들 중 하나 클릭: `get_attribute("href")`
- Scraping
  - Scraping 해야할 곳: `.detail-field`
  - Scraping 값: `.detail-label`, `.detail-content`
> [!NOTE]
> Scraping 부분은 개발자가 어떻게 HTML Tag, class, id를 구성했느냐에 따라서 많은 변경이 있을 수 있는 부분입니다. 

---

Scraping된 데이터들은 다음과 같이 저장되고 외부 API로 보냅니다.
- JSON 저장
  - 전체 데이터를 이어서 저장하는 방식(`--save-total-data`, `--total-filename`)
  - 하나의 리스트 요소를 저장하는 방식(`--save-single-data`, `--single-data-path`, `--single-filename`) 
- 외부 API 전송
  - 저장된 전체 데이터를 외부 API로 전송하는 방식(`--send-total-data`, `--external-url`)
  - 하나의 리스트 요소를 외부 API로 전송하는 방식(`--send-single-data`, `--external-url`)

---

Playwright의 옵션 사용 방법은 다음과 같습니다.
> [!IMPORTANT]
> Selenium과 다르게 Playwright는 옵션을 메서드의 인자로 전달 하기 때문에 Playwright 옵션 설정은 CLI가 아닌 Config 파일을 이용해야 합니다.
- Config 파일 사용
    ```yaml
    playwright:
      options:
        headless: false
        slow_mo: 500
        chromium_sandbox: true
    ```


## Run
1. 브라우저 설치
   ```shell
    sudo playwright install-deps
    playwright install chromium # firefox, webkit
   ```
2. 의존성 설치
    ```shell
    pip install --upgrade pip
    pip install --no-cache-dir -r requirements.txt
    ```
3. Scraping 실행
    ```shell
    python main.py -c scrap-config.yml
    ```

## Otions

> [!IMPORTANT]
> CLI > YAML > 기본값 순으로 우선순위를 가집니다.
> (CLI와 YAML에 같은 값이 있어도 CLI의 값을 우선합니다.)

| CLI 옵션                                | Config Key (YAML)           | 기본값                    | 설명                               |
|---------------------------------------|-----------------------------|------------------------|----------------------------------|
| `-c`, `--config`                      | *(없음)*                      | `None`                 | 설정 파일(`.yml`) 경로                 |
| `--data-root-path`                    | `data_root_path`            | `"applications"`       | 데이터 저장 루트 경로                     |
| `--file-extension`                    | `file_extension`            | `".json"`              | 저장할 파일 확장자                       |
| `--total-filename`                    | `total.filename`            | `"total-applications"` | 전체 데이터를 저장할 파일명 (확장자 제외)         |
| `--username`                          | `username`                  | `None`                 | 로그인 사용자명                         |
| *(CLI 없음)*                            | `password`                  | `입력 요청`                | 로그인 비밀번호 (CLI에서는 입력받음)           |
| `--url`                               | `playwright.url`            | `None`                 | 접속할 대상 URL                       |
| `--external-url`                      | `external_url`              | `None`                 | 외부 API URL                       |
| `--single-data-path`                  | `single.path`               | `username`             | 개별 데이터 저장 경로 (data-root-path 내부) |
| `--single-filename`                   | `single.filename`           | `"single-application"` | 개별 데이터를 저장할 파일명 (확장자 제외)         |
| `--save-single-data` (`true`/`false`) | `single.save`               | `False`                | 개별 데이터 저장 여부                     |
| `--send-single-data` (`true`/`false`) | `single.send`               | `False`                 | 개별 데이터 전송 여부                     |
| `--save-total-data` (`true`/`false`)  | `total.save`                | `False`                 | 전체 데이터 저장 여부                     |
| `--send-total-data` (`true`/`false`)  | `total.send`                | `False`                 | 전체 데이터 전송 여부                     |
| `--is-test` (`true`/`false`)          | `is_test`                  | `False`                 | 테스트 여부                           |
| *(CLI 없음)*                            | `playwright.options` (딕셔너리) | `[]`                   | Playwright 브라우저 옵션               |

## Selenium VS Playwright

1000개의 데이터를 Scraping 했을 때의 성능 비교입니다.

|     | Selenium  | Playwright |
| :-: |:---------:| :-: |
| 작업시간 | 250.819초  | 68.441초 |
| 메모리 | 390.87MB  | 12.61MB |
| 네트워크 | 3055.77MB | 27.37MB |