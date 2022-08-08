from enum import Enum


class Response:
    class ResponseType(Enum):
        RequestVote = 1
        AppendEntity = 2

    def __init__(self, node_id: int, term: int, success: bool, response_type: str):
        self.term = term
        self.node_id = node_id
        self.success = success
        self.type = self.ResponseType[response_type]

    def get_term(self):
        return self.term

    def get_id(self):
        return self.node_id

    def is_success(self):
        return self.success
