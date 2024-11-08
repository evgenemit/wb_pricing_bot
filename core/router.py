from aiogram import Router, F
from aiogram.filters.command import Command

from core.handlers import basic, product
from core.states import AddProductStates, UpdateProductStates


core_router = Router()
core_router.startup.register(basic.startup)
core_router.shutdown.register(basic.shutdown)
core_router.message.register(product.start, Command('start'))
core_router.message.register(product.add_product, F.text == 'Добавить')
core_router.message.register(product.tracked_products, F.text == 'Отслеживаемые')
core_router.message.register(product.main_menu, F.text == 'Отмена')

core_router.callback_query.register(product.product_update_request, F.data.startswith('pr_update_'))
core_router.callback_query.register(product.product_delete, F.data.startswith('pr_delete_'))
core_router.message.register(product.product_update_price, UpdateProductStates.GET_NEW_PRICE)

core_router.message.register(product.add_product_get_article, AddProductStates.GET_ARTICLE)
core_router.message.register(product.add_product_confirm, AddProductStates.CONFIRM)
core_router.message.register(product.add_product_get_price, AddProductStates.GET_PRICE)
