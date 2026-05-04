
class expInvalidRequest(Exception):
    pass



class expInvalidRequestsResponse(Exception):
    pass




class invalidCredentials(Exception):
    pass



class userNotFound(Exception):
    def __init__(self, message="User not found", request_data=None):
        super().__init__(message)
        self.request_data = request_data



class captchaWrong(Exception):
    pass


class expMaxRetries(Exception):
    pass


class expSpecialTimeOut(Exception):
    pass


class enoughMobile(Exception):
    pass


class ItemNotFound(Exception):
    pass