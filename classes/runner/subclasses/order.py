


class OrderRunner:
    def __init__(self, runner):
        self.runner = runner

    async def _update_order_cache(self):
        '''
        Обновляет кеш заказов в раннере
        '''
        orders = await self.runner.account.profile.get_my_sells(25)
        result = []
        for order in orders:
            o = {
                'id': order.order_id,
                'time': order.order_time,
                'client_name': order.client_name,
                'price': order.price,
                'name': order.name,
                'status': order.status
            }
            result.append(o)
        self.runner.old_orders = self.runner.orders
        self.runner.orders = result

    async def _compare_order_cache(self):
        '''
        Сравнивает старый и новый кеш заказов
        '''
        result = []
        if self.runner.orders != self.runner.old_orders:
            for order in self.runner.orders:
                if order not in self.runner.old_orders:
                    result.append(order)
        return result
