class AppendEntityResponse:
    def __init__(self, success: bool, term: int, node_id: int):
        self.success = success
        self.term = term
        self.id = node_id

    def get_term(self):
        return self.term

    def get_id(self):
        return self.id

    def is_success(self):
        return self.success