"""Фикстуры браузера и вложения отчёта при падении."""

import json
from pathlib import Path

import pytest
import allure
from playwright.sync_api import sync_playwright

from core.config import config
from core.logger import logger, mask


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Маскировать текстовые файлы Allure после завершения записи плагином."""
    output = session.config.getoption("allure_report_dir", default=None)
    if not output:
        return
    for path in Path(output).glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            def sanitize(value):
                if isinstance(value, str):
                    return mask(value)
                if isinstance(value, list):
                    return [sanitize(item) for item in value]
                if isinstance(value, dict):
                    return {key: sanitize(item) for key, item in value.items()}
                return value
            path.write_text(json.dumps(sanitize(data), ensure_ascii=False), encoding="utf-8")
        except (OSError, ValueError) as exc:
            logger.error("Не удалось обезличить файл Allure %s: %s", path.name, exc)
            session.exitstatus = pytest.ExitCode.INTERNAL_ERROR


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        instance = playwright.chromium.launch(headless=config.headless)
        yield instance
        instance.close()


@pytest.fixture
def page(browser):
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    context.set_default_timeout(config.timeout)
    page = context.new_page()
    logger.info("Открыт изолированный браузерный контекст")
    logger.debug("Создан контекст Chromium с размером окна 1440 × 900")
    yield page
    context.close()
    logger.info("Браузерный контекст закрыт")


@pytest.fixture
def authenticated(page):
    from ui.login_page import LoginPage

    if not config.email or not config.password:
        pytest.skip("Укажите TEST_EMAIL и TEST_PASSWORD в .env")
    login = LoginPage(page)
    try:
        login.login(config.email, config.password)
        yield login
    finally:
        if page.locator('a[href="/personal/"]:visible').count():
            login.logout()


@pytest.fixture
def clean_test_cart(authenticated, page):
    from ui.shop_page import ShopPage

    page.goto(f"{config.base_url}/personal/order/", wait_until="domcontentloaded")
    empty_cart = page.get_by_text("Ваша корзина пуста", exact=False)
    try:
        empty_cart.wait_for(state="visible")
    except Exception:
        logger.warning("Корзина не пуста или её состояние не удалось проверить; тест остановлен без удаления товаров")
        raise
    shop = ShopPage(page)
    try:
        yield shop
    finally:
        shop.remove_test_product()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.failed:
        if call.excinfo is not None:
            # Allure использует exconly(), где pytest может хранить исходный текст отдельно.
            call.excinfo.exconly = lambda *args, **kwargs: "Тест завершился ошибкой; подробности см. во вложении «Ошибка»."
        error = mask(report.longreprtext)
        # Allure и терминал получают обезличенный текст вместо исходного traceback.
        report.longrepr = error
        logger.error("Тест %s завершился ошибкой: %s", item.name, error)
        allure.attach(error, name="Ошибка", attachment_type=allure.attachment_type.TEXT)
        log_path = Path("logs/test.log")
        if log_path.exists():
            allure.attach(mask(log_path.read_text(encoding="utf-8")), name="Лог запуска", attachment_type=allure.attachment_type.TEXT)
        page = item.funcargs.get("page")
        if page and not page.is_closed():
            try:
                # Закрываем поля и текст с email; маскирование применяется к снимку,
                # не изменяя состояние страницы.
                # Личный кабинет может показывать произвольные персональные данные вне полей.
                private_page = "/personal/" in page.url
                masks = [page.locator("body" if private_page else "input, textarea")]
                if config.email:
                    masks.append(page.get_by_text(config.email, exact=False))
                screenshot = page.screenshot(mask=masks, animations="disabled")
                allure.attach(screenshot, name="Скриншот", attachment_type=allure.attachment_type.PNG)
            except Exception as exc:
                logger.warning("Не удалось сделать скриншот: %s", exc)
