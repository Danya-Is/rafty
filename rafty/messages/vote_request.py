class VoteRequest:
    def __init__(self, term: int, node_id: int):
        self.term = term
        self.id = node_id

    def get_term(self):
        return self.term

    def get_id(self):
        return self.id
