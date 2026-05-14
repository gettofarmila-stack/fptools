from models.chat import ChatData
from utils.errors import MessageNotDelivered

class ChatManager:
    def __init__(self, account):
        self.account = account

    async def get_chats(self):
        """
        Собирает все чаты на аккаунте.

        Returns:
            list: Список объектов чатов. Каждый содержит:   
                - id (str): ID чата (node_id).  
                - username (str): Имя клиента.  
                - last_msg (str): Последнее сообщение в чате.   
                - date (str): Дата последнего сообщения.    
                - link (str): Полная ссылка на чат. 
                - is_unread (bool): Прочитано или нет (True, если не прочитано).    

        """
        html = await self.account.client.get_chats_page()
        chats = self.account.parser.parse_chats_list(html)
        return chats

    async def send_message(self, chat_id:str, text:str):
        """
        Отправляет сообщение.  

        Args:
            chat_id (str): ID чата  
            text (str): Текст сообщения 

        Returns:
            bool: True, если сообщение отправлено   

        Raises:
            MessageNotDelivered: Если не удалось отправить сообщение.   
        
        """
        if chat_id not in self.account.node_names or not self.account.csrf_token:
            await self.get_chat_data(chat_id)
        response = await self.account.client.send_message_request(self.account.node_names[chat_id], -1, text, self.account.csrf_token)
        inner_response = response.get('response', {})
        if inner_response.get('error') is None:
            return True
        else:
            error_msg = inner_response.get('error', 'Unknown error')
            raise MessageNotDelivered(f'Server returned a error: {error_msg}')

    async def get_chat_data(self, chat_id):
        '''
        Получает данные чата.

        Args:
            chat_id (int | str): Айди чата

        Returns:
            ChatData: Объект с тех. данными чата:   
                - node_name (str): Полный ID переписки, нужный для отправки сообщения (users-8778502-19903068)  
                - csrf_token (str): Нужен для post запросов, сохраняется в кеш self.account.csrf_token  
                - user_id (str): твой ID    
        '''
        html = await self.account.client.get_current_chat(chat_id)
        data = self.account.parser.parse_chat(html)
        chat = ChatData(node_name=data['data-name'], csrf_token=data['csrf-token'], user_id=data['user-id'])
        self.account.node_names[chat_id] = chat.node_name
        self.account.csrf_token = chat.csrf_token
        self.account.user_id = chat.user_id
        return chat