import argparse
import getpass
from pathlib import Path
from test import test
import psutil
import os

from playwright.sync_api import sync_playwright

from src import utils
from src.scrap import Scraper
from src.utils import convert_absolute_path


def main():
    parser = argparse.ArgumentParser(description="Scraper CLI")

    parser.add_argument("-c", "--config", type=str, help="설정 YAML 파일 경로")
    parser.add_argument("--data-root-path", type=str, default=None)
    parser.add_argument("--file-extension", type=str, default=".json")
    parser.add_argument("--total-filename", type=str, default=None, help=".json은 생략")
    parser.add_argument("--username", type=str, default=None)
    parser.add_argument("--url", type=str, default=None)
    parser.add_argument("--external-url", type=str, default=None)
    parser.add_argument(
        "--single-data-path",
        type=str,
        default=None,
        help="data-root-path 안에 생기는 경로",
    )
    parser.add_argument("--single-filename", type=str, default=None)
    parser.add_argument("--save-single-data", choices=["true", "false"], default=None)
    parser.add_argument("--send-single-data", choices=["true", "false"], default=None)
    parser.add_argument("--save-total-data", choices=["true", "false"], default=None)
    parser.add_argument("--send-total-data", choices=["true", "false"], default=None)
    parser.add_argument("--is-test", choices=["true", "false"], default=None)

    args = parser.parse_args()

    # main.py이 있는 폴더가 기준 폴더
    base_path = Path(__file__).resolve().parent

    config = {}
    if args.config:
        config = utils.load_config(base_path / args.config)

    password = (
        config.get("password")
        if config.get("password")
        else getpass.getpass("Password: ")
    )

    # 옵션 우선 순위: CLI > config.yaml > 기본값
    data_root_path = convert_absolute_path(
        base_path,
        Path(args.data_root_path or config.get("data_root_path", "applications")),
    )
    total_filename = args.total_filename or config.get("total", {}).get(
        "filename", "total-applications"
    )
    username = args.username or config.get("username", None)
    url = args.url or config.get("playwright", {}).get("url", None)
    external_url = args.external_url or config.get("external_url", None)
    single_data_path = Path(
        args.single_data_path or config.get("single", {}).get("path", None) or username
    )
    single_filename = args.single_filename or config.get("single", {}).get(
        "filename", "single-application"
    )
    save_single_data = utils.search_not_none(
        utils.str2bool(args.save_single_data),
        config.get("single", {}).get("save", False),
    )
    send_single_data = utils.search_not_none(
        utils.str2bool(args.send_single_data),
        config.get("single", {}).get("send", False),
    )
    save_total_data = utils.search_not_none(
        utils.str2bool(args.save_total_data), config.get("total", {}).get("save", False)
    )
    send_total_data = utils.search_not_none(
        utils.str2bool(args.send_total_data), config.get("total", {}).get("send", False)
    )
    is_test = utils.search_not_none(
        utils.str2bool(args.is_test), config.get("is_test", False)
    )
    playwright_options = config.get("playwright", {}).get("options", {})
    file_extension = args.file_extension or config.get("file_extension", ".json")

    if is_test:
        playwright_options = {"headless": True, "slow_mo": 0, "chromium_sandbox": False}

    scraper = Scraper(data_root_path, total_filename, file_extension)
    scraper.username = username
    scraper.password = password

    with sync_playwright() as p:
        browser_type = p.chromium
        browser = browser_type.launch(
            headless=playwright_options.get("headless", False),
            slow_mo=playwright_options.get("slow_mo", 0),
            chromium_sandbox=playwright_options.get("chromium_sandbox", False),
        )
        context = browser.new_context(base_url=url)
        page = context.new_page()
        page.goto(url)

        process = lambda: scraper.scrap(
            page=page,
            external_url=external_url,
            save_total_data=save_total_data,
            send_total_data=send_total_data,
            save_single_data=save_single_data,
            send_single_data=send_single_data,
            single_data_path=single_data_path,
            single_filename=single_filename,
        )

        if is_test:
            python_pid = os.getpid()
            child_pids = []
            proc = psutil.Process(python_pid)
            for child in proc.children(recursive=True):
                if "headless_shell" in child.name():
                    child_pids.append(child.pid)
            test(process, "playwright", base_path, child_pids[-1])
        else:
            process()
        browser.close()


if __name__ == "__main__":
    main()
