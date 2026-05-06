from bs4 import BeautifulSoup
from models.chat import Chat


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