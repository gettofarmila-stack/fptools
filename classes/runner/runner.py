import asyncio
import httpx
from types import SimpleNamespace

from utils.errors import CriticalRunnerError
from classes.runner.subclasses.chat import ChatRunner
from classes.runner.subclasses.order import OrderRunner

class Runner:
    def __init__(self, account):
        self.account = account
        self.chat = ChatRunner(self)
        self.order = OrderRunner(self)
        self.msgs = []
        self.old_msgs = []
        self.orders = []
        self.old_orders = []
        self.cache_is_updated = False
        #   хендлеры
        self.message_handlers = []
        self.order_handlers = []
        self.on_confirmed_handlers = []
        self.on_new_orders_handlers = []
    
    async def runner_polling(self, timer):
        '''
        Принимает timer - количество секунд, раз в который будет проверка новых событий
        Запускает цикл раннера(поиск событий), раннер сравнивает старый кеш с новым в timer секунд, рекомендуемая задержка 3-5 сек
        '''
        while True:
            try:
                await self.cache_runner()
                await asyncio.sleep(timer)
            except (httpx.ConnectTimeout, httpx.RemoteProtocolError, httpx.ReadTimeout, httpx.ConnectError):
                await asyncio.sleep(timer)
            except Exception as e:
                raise CriticalRunnerError(message=str(e))

    def message_handler(self):
        '''Декоратор возвращает новые сообщения'''
        def decorator(func):
            self.message_handlers.append(func)
            return func
        return decorator

    def order_handler(self):
        '''Декоратор возвращает все события заказов'''
        def decorator(func):
            self.order_handlers.append(func)
            return func
        return decorator
    
    def on_confirmed_handler(self):
        '''Декоратор, который возвращает только событие заказ подтверждён'''
        def decorator(func):
            self.on_confirmed_handlers.append(func)
            return func
        return decorator

    def on_new_order_handler(self):
        '''Декоратор, который возвращает только события новый заказ'''
        def decorator(func):
            self.on_new_orders_handlers.append(func)
            return func
        return decorator

    async def warm_up(self):
        '''Прогрев кеша'''
        for _ in range(2):
            await self.chat.update_chat_cache()
            await self.order.update_order_cache()
        self.cache_is_updated = True

    async def cache_runner(self):
        '''
        Управляет кешем
        '''
        if not self.cache_is_updated:
            await self.warm_up()
            return
        #   проверка чатов
        await self.chat.update_chat_cache()
        chats = await self.chat.compare_chat_cache()
        if chats:
            for handler in self.message_handlers:
                await handler(chats)
        #   проверка заказов
        await self.order.update_order_cache()
        orders = await self.order.compare_order_cache()
        if orders:
            for order in orders:
                for handler in self.order_handlers:
                    await handler(order)
                if order['status'] == 'Закрыт':
                    for handler in self.on_confirmed_handlers:
                        await handler(order)
                elif order['status'] in('Оплачено', 'Оплачен'):
                    for handler in self.on_new_orders_handlers:
                        await handler(order)