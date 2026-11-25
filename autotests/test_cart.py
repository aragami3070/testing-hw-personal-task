"""Проверки добавления товара и пересчёта корзины."""

import allure


@allure.feature("Корзина")
@allure.story("Добавление товара")
def test_add_product_to_empty_cart(clean_test_cart):
    """ТК-М12: выбранный диван добавляется в пустую корзину в количестве 1."""
    shop = clean_test_cart.search_product()
    price = shop.product_price()
    shop.add_to_cart().check_cart_item(price)


@allure.feature("Корзина")
@allure.story("Пересчёт количества")
def test_increase_quantity_recalculates_total(clean_test_cart):
    """ТК-М13: увеличение количества до 2 удваивает сумму позиции и итог."""
    shop = clean_test_cart.search_product()
    price = shop.product_price()
    shop.add_to_cart().check_cart_item(price)
    shop.increase_quantity().check_cart_item(price, quantity=2)
