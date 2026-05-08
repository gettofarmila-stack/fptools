from dataclasses import dataclass, field

@dataclass
class Chat:
    '''
    id: Chat id (node)
    username: Client nickname
    last_msg: Last message in chat
    date: last message date
    link: full chat link (https://funpay.com/chat/?node=id)
    is_unread: Readed or not
    '''
    id: str
    node_msg_id: int
    username: str
    last_msg: str
    date: str
    link: str
    is_unread: bool

@dataclass
class ChatData:
    node_name: str
    csrf_token: str
    user_id: str