


class AddonsManager:
    def __init__(self, account):
        self.account = account

    async def get_game_id(self, category_id: str):
        """
        Получает game_id.

        Args:
            category_id (str | int): ID подкатегории.
                
        Returns:    
            str | int: ID игры.
        """
        html = await self.account.client.lot_menu_by_category(category_id)
        data = self.account.parser.parse_lot_menu(html)
        return data