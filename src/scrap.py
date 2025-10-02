import re
import time

from selenium.webdriver.common.by import By

from src import utils


class Scraper:
    def __init__(self, data_root_path, total_filename, file_extension):
        self.data_root_path = data_root_path
        self.file_extension = file_extension
        self.total_filename = f"{total_filename}{file_extension}"
        self.data = utils.load_data(self.data_root_path, self.total_filename)
        self.next_id = self._calculate_next_id()
        self.total = self._calculate_total_approval()
        self._username = None
        self.__password = None

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def password(self):
        raise AttributeError("읽기는 허용하지 않습니다.")

    @password.setter
    def password(self, value):
        self.__password = value

    def _calculate_next_id(self):
        if self.data:
            max_id = max(item.get("id", 0) for item in self.data)
            return max_id + 1
        return 1

    def _calculate_total_approval(self):
        if self.data:
            return len(self.data)
        return 0

    def _collection_data(self, driver):
        """
        현재 페이지에서 보이는 내용들을 dict 형태로 만듬
        """
        data = {}
        fields = driver.find_elements(By.CSS_SELECTOR, ".detail-field")  # .은 클래스
        for field in fields:
            key = field.find_element(By.CSS_SELECTOR, ".detail-label").text
            value = field.find_element(By.CSS_SELECTOR, ".detail-content").text
            new_key = key.replace(":", "").strip()
            data[self._convert_from_ko_to_en(new_key)] = value

        data["id"] = self.next_id
        data["approver"] = self._username
        print(f"✅ Single Data({self.next_id}) 수집", end="\t")
        return data

    def _convert_from_ko_to_en(self, key):
        lang_ref = {
            "신청자": "applicant",
            "신청날짜": "submitted_date",
            "상태": "status",
            "제목": "title",
            "신청 내역": "content",
        }

        return lang_ref[key]

    def _count_up(self):
        self.total += 1
        self.next_id += 1

    def _data_sort(self):
        self.data.sort(key=lambda item: item["id"])

    def _time_sleep(self, _time=0):
        time.sleep(_time)

    def _make_total_data(self):
        self._data_sort()
        json_data = {"total": self.total, "data": self.data}
        return json_data

    def _login(self, driver):
        driver.find_element(
            By.CSS_SELECTOR, "input[type='text'][name='username'][id='id_username']"
        ).send_keys(self._username)
        self._time_sleep()
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(
            self.__password
        )
        self._time_sleep()
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        print(f"✅ {self.username} 로그인 성공")

    def _move_next_page(self, driver, current_page_urls):
        try:
            last_url = current_page_urls[-1]
            match = re.search(r"page=(\d+)", last_url)
            if match:
                current_page = int(match.group(1))
                next_page = current_page + 1
                new_url = re.sub(r"page=\d+", f"page={next_page}", last_url)
                driver.get(new_url)
        except Exception as e:
            raise e

    def scrap(
        self,
        driver,
        external_url,
        save_total_data,
        send_total_data,
        save_single_data,
        send_single_data,
        single_data_path,
        single_filename,
    ):
        self._time_sleep()  # 페이지 이동

        self._login(driver)  # Login

        self._time_sleep()  # 페이지 이동

        ########## 현재 보이는 페이지에 있는 모든 요소들 따로 저장 해두고 처리(다시 HTML 탐색하지 않음) ##########
        while True:
            approval_items = driver.find_elements(By.CSS_SELECTOR, "ul a")

            if len(approval_items) == 0:
                break

            current_page_urls = []
            for approval_item in approval_items:
                current_page_urls += [approval_item.get_attribute("href")]

            for current_page_url in current_page_urls:
                driver.get(current_page_url)
                print("✅ 리스트 중 하나 클릭", end="\t")

                ##########################################
                single_data = self._collection_data(driver)
                single_data["url"] = current_page_url  # 추가되는 내용 (수정 가능)
                sorted_single_data = dict(
                    sorted(single_data.items(), key=lambda item: item[0])
                )
                self.data.append(sorted_single_data)
                if save_single_data:
                    utils.save(
                        sorted_single_data,
                        self.data_root_path / single_data_path,
                        f"{single_filename}-{self.next_id}{self.file_extension}",
                        1,
                    )
                if send_single_data:
                    utils.send_to_external_api(sorted_single_data, external_url)

                self._count_up()
                print()
                ##########################################

                self._time_sleep()

            self._move_next_page(driver, current_page_urls)

        ##################################################################################################
        total_data = self._make_total_data()
        if save_total_data:
            utils.save(total_data, self.data_root_path, self.total_filename, self.total)
        if send_total_data:
            utils.send_to_external_api(total_data, external_url)
        print()
