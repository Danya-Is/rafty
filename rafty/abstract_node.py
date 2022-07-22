import random
import time
from abc import ABC, abstractmethod

from rafty import Config, AppendEntityResponse, VoteRequest, VoteResponse, AppendEntityRequest


class AbstractNode(ABC):
    time: float
    is_master: bool

    def __init__(self, node_id: int):
        self.quorum = None
        self.id = node_id
        self.is_candidate = False
        self.is_online = True
        self.config = Config()
        self.timeout = random.uniform(0, self.config.max_timeout)
        self.term = 0
        self.votes = 0

    def get_id(self):
        return self.id

    def is_master(self):
        return self.is_master

    def is_online(self):
        return self.is_online

    def set_offline(self):
        self.is_online = False

    def set_online(self):
        self.is_online = True

    def set_cluster_conf(self, quorum):
        self.quorum = quorum
        if self.is_master:
            self.quorum.master_id = self.id

    async def send_append_entity_requests(self):
        for i, (node_id, node) in enumerate(self.quorum.nodes.items()):
            if not node.is_online or node_id == self.id:
                continue
            response = await self.send_append_entity_request(node_id)
            if not response.is_success():
                self.is_master = False
                self.is_candidate = False
                self.term = response.get_term()
                break

    @abstractmethod
    async def send_append_entity_request(self, node_id: int) -> AppendEntityResponse:
        pass

    async def append_entity_response(self, request: AppendEntityRequest) -> AppendEntityResponse:
        if request.get_term() >= self.term:
            self.term = request.get_term()
            self.is_candidate = False
            self.is_master = False
            return AppendEntityResponse(True, self.term, self.id)
        else:
            return AppendEntityResponse(False, self.term, self.id)

    async def send_vote_requests(self):
        self.time = time.time()
        self.is_candidate = True
        while self.is_candidate:
            # новый виток выборов
            self.term += 1
            self.votes = 1
            for i, (node_id, node) in enumerate(self.quorum.nodes.items()):
                if not node.is_online or self.id == node_id:
                    continue
                await self.send_vote_request(node_id)
                if self.votes >= self.quorum.consensus_number:
                    self.is_candidate = False
                    self.is_master = True
                    await self.send_append_entity_requests()
                if time.time() > self.time + self.timeout:
                    break
        if self.is_master:
            self.quorum.master_id = self.id

    @abstractmethod
    async def send_vote_request(self, node_id: int):
        pass

    async def vote_response(self, request: VoteRequest) -> VoteResponse:
        if self.term < request.get_term():
            self.term = request.get_term()
            return VoteResponse(1, self.term, self.id)
        else:
            return VoteResponse(0, self.term, self.id)
