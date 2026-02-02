"""Shufersal grocery shopping automation package."""

from .shufersal_tools import (
    shufersal_initialize_browser,
    shufersal_login,
    shufersal_search_products,
    shufersal_add_to_cart,
    shufersal_view_cart,
    shufersal_remove_from_cart,
    shufersal_update_quantity,
    shufersal_proceed_to_checkout,
    shufersal_get_delivery_slots,
    shufersal_take_screenshot,
    shufersal_close_browser,
)

__all__ = [
    "shufersal_initialize_browser",
    "shufersal_login",
    "shufersal_search_products",
    "shufersal_add_to_cart",
    "shufersal_view_cart",
    "shufersal_remove_from_cart",
    "shufersal_update_quantity",
    "shufersal_proceed_to_checkout",
    "shufersal_get_delivery_slots",
    "shufersal_take_screenshot",
    "shufersal_close_browser",
]
