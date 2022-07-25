from enum import Enum


class Request:
    class RequestType(Enum):
        RequestVote = 1
        AppendEntity = 2

    def __init__(self, node_id: int, term: int, request_type: str):
        self.term = term
        self.id = node_id
        self.type = self.RequestType[request_type]

    def get_term(self):
        return self.term

    def get_id(self):
        return self.id


