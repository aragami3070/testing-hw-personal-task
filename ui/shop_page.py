"""Действия поиска и покупки без отправки заказа."""

import re

import allure
from playwright.sync_api import Page, expect

from core.config import config
from core.logger import logger

PRODUCT = "Амарант А / диван - кровать"
VARIANT = "Parma 25 серый"


class ShopPage:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Найти диван и открыть карточку")
    def search_product(self):
        search = self.page.locator("#search")
        search.fill("Амарант А")
        expect(search).to_have_value("Амарант А")
        self.page.locator(".search__btn").click()
        self.page.get_by_role("link", name=PRODUCT, exact=True).click()
        expect(self.page.locator("h1.card__title1")).to_contain_text(PRODUCT)
        expect(self.page.get_by_text(VARIANT, exact=False).first).to_be_visible()
        expect(self.page.get_by_text("П00484081", exact=False).first).to_be_visible()
        logger.info("Найдена и открыта карточка дивана")
        return self

    @allure.step("Добавить товар и перейти к оформлению")
    def add_to_cart(self):
        self.page.locator("#detail-item__add2cart").click()
        expect(self.page.get_by_text("Товар добавлен в корзину", exact=True)).to_be_visible()
        self.page.get_by_text("Перейти в корзину", exact=True).click()
        expect(self.page.locator("#ORDER_CONFIRM_BUTTON")).to_be_visible()
        logger.info("Открыты корзина и форма оформления")
        return self

    @allure.step("Проверить товар и оформление без отправки заказа")
    def check_checkout(self):
        row = self.page.locator("tr").filter(has_text=PRODUCT)
        expect(row).to_have_count(1)
        expect(row).to_contain_text(VARIANT)
        expect(row.locator('input[name="item_quantity"]')).to_have_value("1")
        expect(row.locator(".price")).not_to_be_empty()
        expect(self.page.locator("#ORDER_PROP_1")).to_be_visible()
        expect(self.page.locator("#ORDER_PROP_3")).to_be_visible()
        expect(self.page.locator("#ORDER_CONFIRM_BUTTON")).to_be_visible()
        logger.info("Состав корзины и форма оформления проверены; заказ не отправлен")

    @allure.step("Запомнить текущую цену товара")
    def product_price(self):
        price = self.page.locator(".card__price-wrap:visible .card__new-price")
        expect(price).to_be_visible()
        return self._parse_price(price.inner_text())

    @staticmethod
    def _parse_price(text):
        digits = "".join(re.findall(r"[0-9]", text))
        assert digits, "Цена товара не содержит цифр"
        return int(digits)

    @allure.step("Проверить добавленный товар и его стоимость")
    def check_cart_item(self, price, quantity=1):
        row = self.page.locator("tr").filter(has_text=PRODUCT)
        expect(row).to_have_count(1)
        expect(row).to_contain_text(VARIANT)
        expect(row.locator('input[name="item_quantity"]')).to_have_value(str(quantity))
        expected_price = rf"^\s*{r'[\s  ]*'.join(str(price * quantity))}\s*₽\s*$"
        expect(row.locator(".price")).to_have_text(re.compile(expected_price))
        expect(self.page.locator(".total-price")).to_have_text(re.compile(expected_price))
        logger.info("Проверены позиция, количество и сумма корзины")
        return self

    @allure.step("Увеличить количество товара на единицу")
    def increase_quantity(self):
        row = self.page.locator("tr").filter(has_text=PRODUCT)
        row.locator(".quant_up").click()
        expect(row.locator('input[name="item_quantity"]')).to_have_value("2")
        logger.info("Количество товара увеличено до двух")
        return self

    @allure.step("Удалить добавленную тестовую позицию")
    def remove_test_product(self):
        self.page.goto(f"{config.base_url}/personal/order/", wait_until="domcontentloaded")
        row = self.page.locator("tr").filter(has_text=PRODUCT)
        if row.count():
            expect(row).to_have_count(1)
            row.locator(".remove_items").click()
            expect(row).to_have_count(0)
            logger.info("Тестовая позиция удалена из корзины")
