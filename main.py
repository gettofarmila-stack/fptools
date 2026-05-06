import httpx

from core.account import Account

class FunPayTools:
    def __init__(self, gkey):
        self.headers = {
            "Cookie": f"golden_key={gkey}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) ..."
        }
        self.client = httpx.AsyncClient(
            http2=True,
            headers=self.headers,
            base_url='https://funpay.com'
        )
        self.account = Account(self.client)
