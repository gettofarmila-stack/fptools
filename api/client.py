



class FunPayClient:
    def __init__(self, http_client):
        self.client = http_client

    async def get_chats_page(self) -> str:
        r = await self.client.get('/chat/')
        return r.text