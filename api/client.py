import json



class FunPayClient:
    def __init__(self, http_client):
        self.client = http_client

    async def get_chats_page(self) -> str:
        r = await self.client.get('/chat/')
        return r.text

    async def get_finance_page(self) -> str:
        r = await self.client.get('/account/balance')
        return r.text

    async def send_message_request(self, node_name, last_msg, text, csrf_token):
        request_data = {
        "action": "chat_message",
        "data": {
            "node": node_name,
            "last_message": last_msg,
            "content": text
        }
    }
        payload = {
            'request': json.dumps(request_data),
            'csrf_token': csrf_token
        }
        headers = {
        "X-Requested-With": "XMLHttpRequest",
        "X-Cp-Csrf-Token": csrf_token,
        "Referer": f"https://funpay.com/chat/?node={node_name.split('-')[-1]}"
    }
        r = await self.client.post('/runner/', data=payload, headers=headers)
        return r.json()

    async def get_current_chat(self, chat_id):
        r = await self.client.get(f'/chat/?node={chat_id}')
        return r.text

    async def get_user_profile(self, user_id):
        r = await self.client.get(f'/users/{user_id}/')
        return r.text

    async def lot_menu_by_category(self, category_id):
        r = await self.client.get(f'/lots/{category_id}/trade')
        return r.text

    async def get_main_menu(self):
        r = await self.client.get('/')
        return r.text

    async def raise_lot(self, node_id, game_id, csrf_token):
        payload = {
            'game_id': game_id,
            'node_id': node_id,
            'csrf_token': csrf_token
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "X-Cp-Csrf-Token": csrf_token
        }
        r = await self.client.post('/lots/raise', data=payload, headers=headers)
        if "application/json" in r.headers.get("Content-Type", ""):
            response = r.json()
            return response.get('msg')
        else:
            return {"error": "not_json", "status": r.status_code}
            
    async def get_lot_info(self, lot_id):
        r = await self.client.get(f'/lots/offer?id={lot_id}')
        return r.text

    async def get_my_sells(self):
        r = await self.client.get('/orders/trade')
        return r.text

    async def refund_order(self, csrf_token, order_id):
        url = f'/orders/refund'
        payload = {
            'csrf_token': csrf_token,
            'id': order_id
        }
        r = await self.client.post(url, data=payload)
        return r

    async def get_order_info(self, order_id):
        r = await self.client.get(f'/orders/{order_id}/')
        return r.text

    async def get_lot_editor_data(self, lot_id):
        r = await self.client.get(f'/lots/offerEdit?offer={lot_id}')
        return r.text

    async def edit_lot(self, lot, active=None):
        payload = {
            'csrf_token': lot.csrf_token,
            'form_created_at': lot.form_created_at,
            'offer_id': lot.offer_id,
            'node_id': lot.node_id,
            'location': lot.location,
            'deleted': lot.deleted,
#            'secrets': lot.secrets,
#            'price': lot.price,
#            'amount': lot.amount
        }
        payload.update(lot.fields)
        if active:
            payload['active'] = 'on'
        r = await self.client.post('/lots/offerSave', data=payload)
        return r