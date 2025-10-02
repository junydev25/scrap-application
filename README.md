# Scrap Application

## Description
해당 Scraping은 Selenium을 사용하므로 특정 브라우저의 드라이버를 설치해야 합니다. 해당 프로젝트에서는 크롬 드라이버를 설치하여 사용했으며 버전과 중요 환경은 다음과 같습니다.
```markdown
OS: Ubuntu 24.04.1 LTS
Chrome Driver: 140.0.7339.185
Selenium: 4.35.0
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

Selenium의 Chrome Driver 옵션 사용 방법은 다음과 같습니다.
- CLI 사용시
    ```shell
    python main.py --selenium-options "--headless,--disable-gpu,--no-sandbox,--disable-dev-shm-usage"
    ```
- Config 파일 사용시
    ```yaml
    selenium:
      driver:
        options:
          - "--disable-gpu"
          - "--no-sandbox"
          - "--disable-dev-shm-usage"
    ```


## Run
1. Chrome Driver 설치 및 확인
   ```shell
   sudo apt install -y chromium-chromedriver 2:1snap1-0ubuntu2
   which chromedriver # --driver-path에 사용
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

| CLI 옵션                                | Config Key (YAML)               | 기본값                    | 설명                                                |
|---------------------------------------|---------------------------------|------------------------|---------------------------------------------------|
| `-c`, `--config`                      | *(없음)*                          | `None`                 | 설정 파일(`.yml`) 경로                                  |
| `--data-root-path`                    | `data_root_path`                | `"applications"`       | 데이터 저장 루트 경로                                      |
| `--file-extension`                    | `file_extension`                | `".json"`              | 저장할 파일 확장자                                        |
| `--total-filename`                    | `total.filename`                | `"total-applications"` | 전체 데이터를 저장할 파일명 (확장자 제외)                          |
| `--username`                          | `username`                      | `None`                 | 로그인 사용자명                                          |
| *(CLI 없음)*                            | `password`                      | `입력 요청`                | 로그인 비밀번호 (CLI에서는 입력받음)                            |
| `--driver-path`                       | `selenium.driver.path`          | `None`                 | Selenium WebDriver 실행 파일 경로                       |
| `--url`                               | `selenium.url`                  | `None`                 | 접속할 대상 URL                                        |
| `--external-url`                      | `external_url`                  | `None`                 | 외부 API URL                                        |
| `--single-data-path`                  | `single.path`                   | `username`             | 개별 데이터 저장 경로 (data-root-path 내부)                  |
| `--single-filename`                   | `single.filename`               | `"single-application"` | 개별 데이터를 저장할 파일명 (확장자 제외)                          |
| `--save-single-data` (`true`/`false`) | `single.save`                   | `False`                | 개별 데이터 저장 여부                                      |
| `--send-single-data` (`true`/`false`) | `single.send`                   | `False`                 | 개별 데이터 전송 여부                                      |
| `--save-total-data` (`true`/`false`)  | `total.save`                    | `False`                 | 전체 데이터 저장 여부                                      |
| `--send-total-data` (`true`/`false`)  | `total.send`                    | `False`                 | 전체 데이터 전송 여부                                      |
| `--is-test` (`true`/`false`)          | `is_test`                       | `False`                 | 테스트 여부                                            |
| `--selenium-options` (쉼표 구분)          | `selenium.driver.options` (리스트) | `[]`                   | Selenium 브라우저 옵션 (예: `"--headless,--no-sandbox"`) |
