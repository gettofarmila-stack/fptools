from utils.errors import RequestError, LotEditingError


class FunPayEditor:
    def __init__(self, account):
        self.account = account

    async def change_lot_price(self, lot_id, new_price: str):
        '''
        Изменяет цену лота.

        Args:
            lot_id (str | int): Айди лота
            new_price (str): Новая цена лота
        Returns:
            bool: True - цена изменилась.
        Raises:
            LotEditingError: Цена не изменилась 
            RequestError: Плохое соединение с интернетом/сервер не ответил
        '''
        lot = await self.account.lot._get_lot_editor_details(lot_id)
        lot.fields['price'] = new_price
        response = await self.account.client.edit_lot(lot, active=True)
        if response.status_code == 200:
            new_lot = await self.account.lot._get_lot_editor_details(lot_id)
            if new_lot.fields['price'] == lot.fields['price']:
                return True
            raise LotEditingError('Changing lot price error')
        raise RequestError()

    async def toggle_off_lot(self, lot_id):
        '''
        Выключает лот.

        Args:
            lot_id (str | int): Айди лота
        Returns:
            bool: True - лот выключен
        Raises:
            RequestError: Сервер не ответил
        '''
        lot = await self.account.lot._get_lot_editor_details(lot_id)
        response = await self.account.client.edit_lot(lot)
        if response.status_code == 200:
            return True
        raise RequestError()

    async def toggle_on_lot(self, lot_id):
        '''
        Включает лот.

        Args:
            lot_id (str | int): Айди лота
        Returns:
            bool: True - лот включен
        Raises:
            RequestError: Сервер не ответил
        '''
        lot = await self.account.lot._get_lot_editor_details(lot_id)
        response = await self.account.client.edit_lot(lot, active=True)
        if response.status_code == 200:
            return True
        raise RequestError()