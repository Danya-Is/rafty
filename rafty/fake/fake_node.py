import time

from rafty import Request, Response, AbstractNode


class FakeNode(AbstractNode):

    def __init__(self, node_id: int, is_master=False, is_owner=False):
        super().__init__(node_id)
        self.is_master = is_master
        self.is_owner = is_owner

    async def send_vote_request(self, node_id: int):
        response = await self.quorum.nodes[node_id].response(Request(self.id, self.term, 'RequestVote'))
        self.votes += response.is_success()
        if response.get_term() > self.term or \
                (self.quorum.nodes[response.get_id()].is_master and response.get_term() == self.term):
            self.is_candidate = False
            self.votes = 0

    async def send_append_entity_request(self, node_id: int) -> Response:
        return await self.quorum.nodes[node_id].response(Request(self.id, self.term, 'AppendEntity'))
