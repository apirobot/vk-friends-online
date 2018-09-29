class VkError(Exception):
    pass


class Unavailable(VkError):
    pass


class VkMethodError(VkError):
    def __init__(self, code, message):
        self.code = code
        self.message = message
