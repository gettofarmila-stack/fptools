import json
from bs4 import BeautifulSoup
from models.chat import ChatData
from models.account import LotInfo, Profile, UserData, Order
from models.lots import CurrentLotInfo, LotEditor
from api.client import FunPayClient
from api.parsers import FunPayParser
from utils.errors import MessageNotDelivered, RaisingLotError, FunPayRefundError, RequestError


class Account:
    def __init__(self, client):
        self.http_client = client
        self.client = FunPayClient(self.http_client)
        self.parser = FunPayParser()
        self.user_id = None
        self.csrf_token = None
        self.last_msg_ids = {}
        self.node_names = {}


#       ░█████╗░██╗░░██╗░█████╗░████████╗
#       ██╔══██╗██║░░██║██╔══██╗╚══██╔══╝
#      ██║░░╚═╝███████║███████║░░░██║░░░
#     ██║░░██╗██╔══██║██╔══██║░░░██║░░░
#    ╚█████╔╝██║░░██║██║░░██║░░░██║░░░
#   ░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░

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

#         ░█████╗░██████╗░██████╗░░█████╗░███╗░░██╗░██████╗
#        ██╔══██╗██╔══██╗██╔══██╗██╔══██╗████╗░██║██╔════╝
#       ███████║██║░░██║██║░░██║██║░░██║██╔██╗██║╚█████╗░
#      ██╔══██║██║░░██║██║░░██║██║░░██║██║╚████║░╚═══██╗
#     ██║░░██║██████╔╝██████╔╝╚█████╔╝██║░╚███║██████╔╝
#    ╚═╝░░╚═╝╚═════╝░╚═════╝░░╚════╝░╚═╝░░╚══╝╚═════╝░

    async def get_game_id(self, category_id):
        '''
        https://funpay.com/lots/{category_id}/trade
        '''
        html = await self.client.lot_menu_by_category(category_id)
        data = self.parser.parse_lot_menu(html)
        return data

#         ██████╗░██████╗░░█████╗░███████╗██╗██╗░░░░░███████╗
#        ██╔══██╗██╔══██╗██╔══██╗██╔════╝██║██║░░░░░██╔════╝
#       ██████╔╝██████╔╝██║░░██║█████╗░░██║██║░░░░░█████╗░░
#      ██╔═══╝░██╔══██╗██║░░██║██╔══╝░░██║██║░░░░░██╔══╝░░
#     ██║░░░░░██║░░██║╚█████╔╝██║░░░░░██║███████╗███████╗
#    ╚═╝░░░░░╚═╝░░╚═╝░╚════╝░╚═╝░░░░░╚═╝╚══════╝╚══════╝

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

    async def get_my_sells(self, limit:int=0):
        '''
        Accept limit of orders arg, can be null(return all orders)
        Func get https://funpay.com/orders/trade
        Returns list of objects with orders
            order_id: str
            order_time: str
            client_name: str
            price: float
            status: str
            name: str
            category: str
        '''
        html = await self.client.get_my_sells()
        data = self.parser.parse_my_sells(html)
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
        Function gets user info  
        Takes user_id, nullable  
        If user_id is null, the value will be your session user_id  
        Returns object with 
            category_ids(node_id)
            lots[{lot['name']: lot['id']}]
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
    
#         ░█████╗░██████╗░██████╗░███████╗██████╗░
#        ██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
#       ██║░░██║██████╔╝██║░░██║█████╗░░██████╔╝
#      ██║░░██║██╔══██╗██║░░██║██╔══╝░░██╔══██╗
#     ╚█████╔╝██║░░██║██████╔╝███████╗██║░░██║
#    ░╚════╝░╚═╝░░╚═╝╚═════╝░╚══════╝╚═╝░░╚═╝

    async def get_order_details(self, order_id):
        '''
        Func get data in /orders/{order_id}/
        return object with:
            status: str
        '''
        html = await self.client.get_order_info(order_id)
        data = self.parser.parse_order_page(html)
        order = Order(status=data['status'])
        return order

    async def refund_order(self, order_id):
        '''
        Func post data to /orders/refund
        Return True is 200, if error raise FunPayRefundError
        '''
        if not self.csrf_token:
            await self.get_user_data()
        response = await self.client.refund_order(self.csrf_token, order_id)
        if response.status_code == 200:
            s = await self.get_order_details(order_id)
            status = s.status
            if status == 'Возврат':
                return True
            raise FunPayRefundError(f'Cant make refund. Now order status is: {status}')

    
#        ██╗░░░░░░█████╗░████████╗  
#       ██║░░░░░██╔══██╗╚══██╔══╝  
#      ██║░░░░░██║░░██║░░░██║░░░ 
#     ██║░░░░░██║░░██║░░░██║░░░ 
#    ███████╗╚█████╔╝░░░██║░░░ 
#   ╚══════╝░╚════╝░░░░╚═╝░░░ 
    
    async def get_lot_editor_details(self, lot_id):
        '''
        Get data from https://funpay.com/lots/offerEdit?offer={lot_id}
        '''
        html = await self.client.get_lot_editor_data(lot_id)
        data = self.parser.parse_edit_lot_page(html)
        lot = LotEditor(**data)
        return lot

    async def get_lot_info(self, lot_id):
        '''
        Func gets lot data:  
            short_desc: str  
            description: str  
            price: float  
        '''
        html = await self.client.get_lot_info(lot_id)
        data = self.parser.parse_current_lot_menu(html)
        lot = CurrentLotInfo(
            short_desc=data['short_desc'],
            description=data['description'],
            price=float(data['price'])
        )
        return lot

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


#         ███████╗██████╗░██╗████████╗░█████╗░██████╗░
#        ██╔════╝██╔══██╗██║╚══██╔══╝██╔══██╗██╔══██╗
#       █████╗░░██║░░██║██║░░░██║░░░██║░░██║██████╔╝
#      ██╔══╝░░██║░░██║██║░░░██║░░░██║░░██║██╔══██╗
#     ███████╗██████╔╝██║░░░██║░░░╚█████╔╝██║░░██║
#    ╚══════╝╚═════╝░╚═╝░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝

    async def change_lot_price(self, lot_id, new_price):
        '''
        Func charge lot price
        '''
        