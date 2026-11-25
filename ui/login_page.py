"""Действия с формой авторизации и личным кабинетом."""

import allure
from playwright.sync_api import Page, expect

from core.config import config
from core.logger import logger


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.form = page.locator("#auth-form")
        self.email = self.form.locator("#email-auth")
        self.password = self.form.locator("#pwd-auth")
        self.submit_button = self.form.locator("button[type=submit]")
        self.status = self.form.locator(".status")

    @allure.step("Открыть форму входа")
    def open(self):
        self.page.goto(f"{config.base_url}/", wait_until="domcontentloaded")
        self.page.locator('[data-target="#auth"]').click()
        expect(self.form).to_be_visible()
        consent = self.page.locator("#block_text_2")
        if not consent.is_checked():
            self.page.locator('label[for="block_text_2"]').click(position={"x": 5, "y": 5})
        logger.info("Открыта форма входа")
        return self

    def fill(self, email: str, password: str):
        self.email.fill(email)
        self.password.fill(password)
        logger.info("Заполнены поля авторизации")
        return self

    @allure.step("Отправить форму входа")
    def submit(self):
        self.submit_button.click()
        logger.info("Отправлена форма авторизации")
        return self

    def login(self, email: str, password: str):
        self.open().fill(email, password).submit()
        self.page.wait_for_url("**/personal/**")
        expect(self.page.locator('a[href="/personal/"]:visible').first).to_be_visible()
        logger.info("Вход выполнен")
        return self

    @allure.step("Выйти из личного кабинета")
    def logout(self):
        self.page.goto(f"{config.base_url}/personal/", wait_until="domcontentloaded")
        logout = self.page.locator('a[href="/?logout=yes"]')
        expect(logout).to_have_count(1)
        logout.click()
        self.page.locator('[data-target="#auth"]').wait_for(state="visible")
        logger.info("Выход выполнен")
