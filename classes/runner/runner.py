import asyncio
import httpx
from types import SimpleNamespace

from utils.errors import CriticalRunnerError
from classes.runner.subclasses.chat import ChatRunner
from classes.runner.subclasses.order import OrderRunner
from classes.runner.subclasses.review import ReviewRunner

class Runner:
    def __init__(self, account):
        self.account = account
        self.chat = ChatRunner(self)
        self.order = OrderRunner(self)
        self.review = ReviewRunner(self)
        #   кеш
        self.msgs = []
        self.old_msgs = []
        self.orders = []
        self.old_orders = []
        self.reviews = []
        self.old_reviews = []
        self.cache_is_updated = False
        #   хендлеры
        self.message_handlers = []
        self.order_handlers = []
        self.on_confirmed_handlers = []
        self.on_new_orders_handlers = []
        self.on_new_review_handlers = []
        self.on_refunded_handlers = []

    async def idle(self):
        """
        Зацикливает выполнение программы, чтобы фоновые задачи не закрылись.
        """
        while True:
            await asyncio.sleep(3600)
    
    async def _run_loop(self, timer):
        while True:
            try:
                await self.cache_runner()
                await asyncio.sleep(timer)
            except (httpx.ConnectTimeout, httpx.RemoteProtocolError, httpx.ReadTimeout, httpx.ConnectError):
                await asyncio.sleep(timer)
            except Exception as e:
                raise CriticalRunnerError(message=str(e))

    async def runner_polling(self, timer, is_background:bool=False):
        '''
        Запускает поиск новых событий.

        Args:
            timer (str): Задержка в секундах, раз в которую будет происходить обновление кеша (рекомендуемо 3-5 сек).   
            is_background (bool): По дефолту True(в фоне). Определяет, будет ли функция запущена в фоне или нет (если не в фоне, блокирует остальные процессы). 
        '''
        if is_background:
            asyncio.create_task(self._run_loop(timer))
        else:
            await self._run_loop(timer)

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
    
    def on_new_review_handler(self):
        '''Декоратор отслеживает новые отзывы'''
        def decorator(func):
            self.on_new_review_handlers.append(func)
            return func
        return decorator

    def on_refunded_handler(self):
        '''Декоратор отслеживает возвраты заказов'''
        def decorator(func):
            self.on_refunded_handlers.append(func)
            return func
        return decorator

    async def _warm_up(self):
        '''Прогрев кеша'''
        for _ in range(2):
            await self.chat._update_chat_cache()
            await self.order._update_order_cache()
            await self.review._update_review_cache()
        self.cache_is_updated = True

    async def cache_runner(self):
        '''Управляет кешем'''
        if not self.cache_is_updated:
            await self._warm_up()
            return
        #   проверка чатов
        await self.chat._update_chat_cache()
        chats = await self.chat._compare_chat_cache()
        if chats:
            for handler in self.message_handlers:
                await handler(chats)
        #   проверка заказов
        await self.order._update_order_cache()
        orders = await self.order._compare_order_cache()
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
                elif order['status'] == 'Возврат':
                    for handler in self.on_refunded_handlers:
                        await handler(order)
        await self.review._update_review_cache()
        reviews = await self.review._compare_review_cache()
        if reviews:
            for handler in self.on_new_review_handlers:
                await handler(reviews)
'''
Переписать документации на русский и со всеми стилями в editor, lot, order, profile, review. Улучшить архитектуру раннера(вынести декораторы в отдельный подкласс), сделать отслеживание новых отзывов в декоратор, запрос и парсинг любой категории (для демперов). Добавить в конфиг клиента поддержку прокси.
'''