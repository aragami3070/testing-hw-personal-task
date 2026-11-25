"""Авторизация: ТК-А02, ТК-А03–А07."""

import allure
import pytest
from playwright.sync_api import expect

from core.config import config
from ui.login_page import LoginPage


@allure.feature("Авторизация")
@allure.story("Успешный вход")
def test_login_by_email(authenticated, page):
    """ТК-А02: вход существующего пользователя по email и паролю."""
    expect(page.locator('a[href="/personal/"]:visible').first).to_be_visible()


@allure.feature("Авторизация")
@allure.story("Негативные сценарии")
@pytest.mark.parametrize(
    ("case", "expected"),
    [
        ("empty_email", "Вы не указали e-mail"),
        ("empty_password", "Вы не указали пароль"),
        ("invalid_format", "Неверный логин или пароль"),
        ("unknown_email", "Пользователь не существует"),
        ("wrong_password", "Неверный логин или пароль"),
    ],
    ids=["empty-email", "empty-password", "invalid-format", "unknown-email", "wrong-password"],
)
def test_login_errors(page, case, expected):
    """ТК-А03–А05, А07: видимое сообщение и отсутствие входа."""
    inputs = {
        "empty_email": ("", "sample-password"),
        "empty_password": ("example@example.org", ""),
        "invalid_format": ("not-an-email", "sample-password"),
        "unknown_email": ("not-existing-731822@example.org", "sample-password"),
    }
    if case == "wrong_password":
        if not config.email or not config.password:
            pytest.skip("Укажите TEST_EMAIL и TEST_PASSWORD в .env")
        wrong_password = "incorrect-test-password-927461"
        if wrong_password == config.password:
            wrong_password += "-other"
        inputs[case] = (config.email, wrong_password)
    login = LoginPage(page).open().fill(*inputs[case])
    with page.expect_response(lambda response: "/ajax/ajax.php" in response.url and response.request.method == "POST") as response_info:
        login.submit()
    response = response_info.value
    assert response.ok, "Сервер не обработал запрос входа"
    assert expected in response.text(), "Сервер вернул неожиданную ошибку входа"
    expect(login.form).to_be_visible()
    expect(login.status, "Сервер вернул ошибку, но форма не показала её пользователю").to_contain_text(expected, timeout=5000)
