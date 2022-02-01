class Request():
    def __init__(self, requestData, requestType, requestPriority) -> None:
        self.requestData = requestData
        self.requestType = requestType
        self.requestPriority = requestPriority
        pass

    def get_request_data(self):
        return self.requestData

    def get_request_type(self):
        return self.requestType

    def get_request_priority(self):
        return self.requestPriority