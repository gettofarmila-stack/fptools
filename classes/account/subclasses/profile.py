from models.account import UserData, Order, Profile, CurReview
from models.lots import LotInfo


class ProfileManager:

    def __init__(self, account):
        self.account = account

    async def get_user_data(self):
        '''
        Запрашивает данные юзера, сохраняет их в кеш.
        
        Returns:
            UserData: Объект с данными юзера:   
                - user_id (str): ID юзера.  
                - csrf_token (str): Нужен для любого post запроса на funpay.    
        '''
        html = await self.account.client.get_main_menu()
        data = self.account.parser.parse_main_menu(html)
        self.account.user_id = data['user-id']
        self.account.csrf_token = data['csrf-token']
        user_data = UserData(csrf_token=data['csrf-token'], user_id=data['user-id'])
        return user_data

    async def get_my_sells(self, limit:int=0):
        '''
        Запрашивает страницу продаж юзера.

        Args:
            limit (int): Лимит заказов, которые нужно вернуть(если 0, то вернёт все заказы).
        Returns:
            list: Список объектов, каждый содержит в себе:  
                - order_id (str): ID заказа.    
                - order_time (str): Время создания заказа.  
                - client_name (str): Имя клиента.   
                - price (float): Сумма заказа.  
                - status (str): Статус заказа.  
                - name (str): Название заказа.  
                - category (str): Категория заказа.     
        '''
        html = await self.account.client.get_my_sells()
        data = self.account.parser.parse_my_sells(html)
        counter = 0
        result = []
        if limit > 0:
            counter += 1
        for i in data:
            if limit != 0 and counter > limit:
                break
            order = Order(
                order_id=i['order-id'],
                order_time=i['order-time'],
                client_name=i['client-name'],
                price=i['price'],
                status=i['status'],
                name=i['name'],
                category=i['category']
            )
            result.append(order)
            counter += 1
        return result

    async def profile(self, user_id=None):
        '''
        Запрашивает профиль юзера.
        Args:
            user_id (str | int): Можно не передавать, если None, сама узнает айди владельца сессии и запросит данные о нём. Айди юзера.
        Returns:
            Profile: Объект, с данными:  
                - category_ids (list): ID категорий, в которых у юзера выставлены лоты.   
                - lots (list): Список словарей с лотами юзера юзера {lot['name']: lot['id']}.   
                - reviews (list): Список объектов отзыва CurReview с данными:  
                    - text (str): Текст отзыва. 
                    - stars (int): Кол-во звёзд в отзыве (1-5). 
                    - author (str): Автор отзыва.   
                    - item_name (str): Название заказа, под которым оставлен отзыв. 
        '''
        target_id = user_id or self.account.user_id
        if not target_id:
            target = await self.get_user_data()
            target_id = target.user_id
        html = await self.account.client.get_user_profile(target_id)
        data = self.account.parser.parse_profile(html)
        lots_list = [LotInfo(name=lot['name'], id=lot['id']) for lot in data['lots']]
        reviews = [CurReview(text=rev['text'], stars=rev['stars'], author=rev['author'], item_name=rev['detail']) for rev in data['reviews']]
        profile = Profile(category_ids=data['category-ids'], lots=lots_list, reviews=reviews)
        return profile

    async def get_balance(self):
        '''
        Собирает баланс аккаунта.

        Returns:
            Balance: Объект с валютами:    
                - rub (float): Баланс в рублях  
                - usd (float): Баланс в долларах  
                - eur (float): Баланс в евро
        '''
        html = await self.account.client.get_finance_page()
        balance = self.account.parser.parse_finanses(html)
        return balance