import httpx
from bs4 import BeautifulSoup
from models.chat import Chat
from api.client import FunPayClient
from api.parsers import FunPayParser


class Account:
    def __init__(self, client):
        self.http_client = client
        self.client = FunPayClient(self.http_client)
        self.parser = FunPayParser()
        self.last_msg_ids = {}

    async def get_chats(self):
        html = await self.client.get_chats_page()
        chats = self.parser.parse_chats_list(html)
        for chat in chats:
            if chat.id not in self.last_msg_ids:
                self.last_msg_ids[chat.id] = chat.node_msg_id
        return chats