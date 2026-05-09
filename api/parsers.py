
import json
from bs4 import BeautifulSoup

from models.chat import Chat
from models.account import Balance
from utils.errors import NullData, ParseException

class FunPayParser:

    @staticmethod
    def parse_chats_list(html_content: str) -> list[Chat]:
        soup = BeautifulSoup(html_content, 'html.parser')
        items = soup.find_all('a', class_='contact-item')
        chats = []
        for item in items:
            href = item.get('href', '')
            node_msg_id = item.get('data-node-msg', '0')
            chat_id = href.split('node=')[-1] if 'node=' in href else ''
            username = item.find('div', class_='media-user-name').text.strip()
            last_msg = item.find('div', class_='contact-item-message').text.strip()
            date = item.find('div', class_='contact-item-time').text.strip()
            is_unread = 'unread' in item.get('class', [])

            chats.append(Chat(
                id=chat_id, node_msg_id=int(node_msg_id), username=username, last_msg=last_msg,
                date=date, link=href, is_unread=is_unread
            ))
        return chats

    @staticmethod
    def parse_finanses(html_content: str):
        soup = BeautifulSoup(html_content, 'html.parser')
        balances_container = soup.find('span', class_='balances-list')
        if not balances_container:
            raise NullData()
        values = balances_container.find_all('span', class_='balances-value')
        clean_values = [v.text.strip() for v in values]
        data = {}
        for i in clean_values:
            value = i.replace('₽', '').replace('$', '').replace('€', '').replace(',', '.').strip()
            num = float(value)
            if '₽' in i: data['rub'] = num
            elif '$' in i: data['usd'] = num
            elif '€' in i: data['eur'] = num
        return Balance(**data)

    @staticmethod
    def parse_chat(html_content: str):
        soup = BeautifulSoup(html_content, 'html.parser')
        try:
            result = {}
            chat_div = soup.find('div', class_='chat')
            if chat_div:
                result['data-name'] = chat_div.get('data-name', '')
            else:
                raise NullData('Chat block is not found')
            body = soup.find('body')
            if not body:
                raise NullData('Body tag is not found')
            app_data_str = body.get('data-app-data', '{}')
            app_data = json.loads(app_data_str)
            result['csrf-token'] = app_data.get('csrf-token', '')
            result['user-id'] = app_data.get('userId', '')
            return result
        except Exception as e:
            raise

    @staticmethod
    def parse_profile(html_content: str):
        soup = BeautifulSoup(html_content, 'html.parser')
        offer_list = soup.find_all('div', class_='offer')
        category_ids = set()
        lots = []
        for offer in offer_list:
            links = offer.find_all('a', href=True)
            for link in links:
                href = link['href']
                if '/lots/' in href and 'id=' not in href:
                    cat_id = href.strip('/').split('/')[-1]
                    if cat_id.isdigit():
                        category_ids.add(cat_id)
                if 'id=' in href:
                    lot_id = href.split('id=')[-1].split('&')[0]
                    name_tag = link.find('div', class_='tc-desc-text')
                    name = name_tag.get_text(strip=True) if name_tag else "Unknown"
                    lots.append({'name': name, 'id': lot_id})
        return {'category-ids': list(category_ids), 'lots': lots}
        
    @staticmethod
    def parse_lot_menu(html_content: str):
        soup = BeautifulSoup(html_content, 'html.parser')
        try:
            button = soup.find('button', class_='js-lot-raise')
            if button:
                return button.get('data-game')
            raise NullData()
        except Exception as e:
            raise ParseException()

    @staticmethod
    def parse_main_menu(html_content: str):
        soup = BeautifulSoup(html_content, 'html.parser')
        user_link = soup.find('a', class_='user-link-dropdown')
        result = {}
        if user_link:
            href = user_link.get('href', '')
            user_id = href.strip('/').split('/')[-1]
            result['user-id'] =  user_id
        else:
            raise NullData()
        body = soup.find('body')
        if not body:
            raise NullData('Body tag is not found')
        app_data_str = body.get('data-app-data', '{}')
        app_data = json.loads(app_data_str)
        result['csrf-token'] = app_data.get('csrf-token', '')
        return result
        
    @staticmethod
    def parse_current_lot_menu(html_content):
        result = {}
        soup = BeautifulSoup(html_content, 'html.parser')
        param_items = soup.find_all('div', class_='param-item')
        descriptions = {}
        for item in param_items:
            header = item.find('h5').get_text(strip=True)
            text = item.find('div').get_text(separator='\n', strip=True)
            descriptions[header] = text
        result['short_desc'] = descriptions.get('Краткое описание')
        result['description'] = descriptions.get('Подробное описание')
        sbp_option = soup.find('option', value='21')
        if sbp_option:
            inner_html = sbp_option.get('data-content')
            if inner_html:
                inner_soup = BeautifulSoup(inner_html, 'html.parser')
                price_span = inner_soup.find('span', class_='payment-value')
                if price_span:
                    raw_price = price_span.get_text(strip=True)
                    result['price'] = raw_price.replace('₽', '').replace('\xa0', '').replace(' ', '').strip()
                    return result
        raise NullData('Parse current lot menu dont have needed data')