from aiogram import Router, F
from aiogram.filters.command import Command

from core.handlers import basic, product, admin
from core.states import AddProductStates, UpdateProductStates, SendMessage
from core.services.answers import answers


core_router = Router()
core_router.startup.register(basic.startup)
core_router.message.register(product.start, Command('start'))
core_router.message.register(product.add_product, F.text.in_((answers['ru']['btn2'], answers['by']['btn2'])))
core_router.message.register(product.tracked_products, F.text.in_((answers['ru']['btn1'], answers['by']['btn1'])))
core_router.message.register(product.main_menu, F.text.in_((answers['ru']['btn3'], answers['by']['btn3'])))
core_router.message.register(product.settings, F.text.in_((answers['ru']['btn9'], answers['by']['btn9'])))
core_router.message.register(admin.get_logs, F.text == 'Логи')
core_router.message.register(admin.get_message, F.text == 'Отправить сообщение')

core_router.callback_query.register(product.product_update_request, F.data.startswith('pr_update_'))
core_router.callback_query.register(product.product_delete, F.data.startswith('pr_delete_'))
core_router.callback_query.register(product.lang_settings, F.data.startswith('lang_'))
core_router.message.register(product.product_update_price, UpdateProductStates.GET_NEW_PRICE)

core_router.message.register(product.add_product_get_article, AddProductStates.GET_ARTICLE)
core_router.message.register(product.add_product_confirm, AddProductStates.CONFIRM)
core_router.message.register(product.add_product_get_price, AddProductStates.GET_PRICE)
core_router.message.register(admin.send_message, SendMessage.GET_TEXT)
