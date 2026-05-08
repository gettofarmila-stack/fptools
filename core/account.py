
from bs4 import BeautifulSoup
from models.chat import ChatData
from models.account import LotInfo, Profile, UserData
from api.client import FunPayClient
from api.parsers import FunPayParser
from utils.errors import MessageNotDelivered, RaisingLotError


class Account:
    def __init__(self, client):
        self.http_client = client
        self.client = FunPayClient(self.http_client)
        self.parser = FunPayParser()
        self.user_id = None
        self.csrf_token = None
        self.last_msg_ids = {}
        self.node_names = {}

    async def get_chats(self):
        '''

        The function calls the chats in account, returns an object with values:  
        id: str, Chat id (node)  
        username: str, Client nickname  
        last_msg: str, Last message in chat  
        date: str, last message date  
        link: str, full chat link (https://funpay.com/chat/?node=id)  
        is_unread: bool, Readed or not  
          
        '''
        html = await self.client.get_chats_page()
        chats = self.parser.parse_chats_list(html)
        for chat in chats:
            if chat.id not in self.last_msg_ids:
                self.last_msg_ids[chat.id] = chat.node_msg_id
        return chats

    async def get_balance(self):
        '''

        The function calls the account balance, returns an object with values:  
        rub: float  
        usd: float  
        eur: float  
          
        '''
        html = await self.client.get_finance_page()
        balance = self.parser.parse_finanses(html)
        return balance

    async def send_message(self, chat_id:str, text:str):
        '''
        The function takes chat_id, text.  
        Sends a message to the given chat, on success it returns 'succes', on error it returns the error MessageNotDelivered
        '''
        if chat_id not in self.node_names or not self.csrf_token:
            await self.get_chat_data(chat_id)
        response = await self.client.send_message_request(self.node_names[chat_id], -1, text, self.csrf_token)
        inner_response = response.get('response', {})
        if inner_response.get('error') is None:
            return 'success'
        else:
            error_msg = inner_response.get('error', 'Unknown error')
            raise MessageNotDelivered(f'Server returned a error: {error_msg}')

    async def get_chat_data(self, chat_id):
        '''
        https://funpay.com/chat/?node={chat_id}
        '''
        html = await self.client.get_current_chat(chat_id)
        data = self.parser.parse_chat(html)
        chat = ChatData(node_name=data['data-name'], csrf_token=data['csrf-token'], user_id=data['user-id'])
        self.node_names[chat_id] = chat.node_name
        self.csrf_token = chat.csrf_token
        self.user_id = chat.user_id
        return chat

    async def profile(self, user_id=None):
        '''
        Function gets user info  
        Takes user_id, nullable  
        If user_id is null, the value will be your session user_id  
        Returns object with category_ids, lots[{lot['name']: lot['id']}]
        https://funpay.com/users/{user_id}/  
        '''
        target_id = user_id or self.user_id
        if not target_id:
            target = await self.get_user_data()
            target_id = target.user_id
        html = await self.client.get_user_profile(target_id)
        data = self.parser.parse_profile(html)
        lots_list = [LotInfo(name=lot['name'], id=lot['id']) for lot in data['lots']]
        profile = Profile(category_ids=data['category-ids'], lots=lots_list)
        return profile

    async def get_game_id(self, category_id):
        '''
        https://funpay.com/lots/{category_id}/trade
        '''
        html = await self.client.lot_menu_by_category(category_id)
        data = self.parser.parse_lot_menu(html)
        return data

    async def raise_lots(self):
        '''
        The function raises your lots and returns a response from the FunPay server.
        '''
        if not self.csrf_token:
            await self.get_user_data()
        try:
            profile = await self.profile()
            category_list = profile.category_ids
            if not category_list:
                raise NullData('I cant raise none')
            response = []
            for node_id in category_list:
                game_id = await self.get_game_id(node_id)
                response.append(await self.client.raise_lot(node_id, game_id, self.csrf_token))
            return response
        except Exception as e:
            raise RaisingLotError()

    async def get_user_data(self):
        '''
        Func gets user data, and save it to cache
        user_id
        csrf_token
        '''
        html = await self.client.get_main_menu()
        data = self.parser.parse_main_menu(html)
        self.user_id = data['user-id']
        self.csrf_token = data['csrf-token']
        user_data = UserData(csrf_token=data['csrf-token'], user_id=data['user-id'])
        return user_data