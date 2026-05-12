

class AccountError(Exception):
    def __init__(self, message='Account error'):
        self.message = message
        super().__init__(self.message)

class ParseException(Exception):
    def __init__(self, message='Data parsing error'):
        self.message = message
        super().__init__(self.message)

class NullData(ParseException):
    '''Data is null'''
    message = 'Null Data'

class MessageNotDelivered(AccountError):
    '''Not delivered message error'''
    message = 'Message is not delivered'

class RaisingLotError(AccountError):
    '''Error by raising lots'''
    message = 'Raising lot error'

class FunPayRefundError(AccountError):
    '''Error by refunding order'''
    message = 'Refunding error'

class RequestError(AccountError):
    """Error by get and parsing response"""
    pass

class LotEditingError(AccountError):
    '''Error by editing lot'''
    message = 'Editing error'
