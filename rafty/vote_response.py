class VoteResponse:
    def __init__(self, value: int, term: int, node_id: int):
        self.term = term
        self.id = node_id
        self.value = value

    def get_term(self):
        return self.term

    def get_id(self):
        return self.id

    def get_value(self):
        return self.value
