"""Безопасный сквозной сценарий по ТК-А02, ТК-М02, М10, М12."""

import allure


@allure.feature("Покупка")
@allure.story("Путь до подтверждения заказа")
def test_purchase_until_confirmation(clean_test_cart):
    """Войти, найти товар, проверить карточку, корзину и форму оформления."""
    clean_test_cart.search_product().add_to_cart().check_checkout()
