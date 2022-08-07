import asyncio
import random
import time
from abc import ABC, abstractmethod

from rafty import Request, Response, Timer, Config


class AbstractNode(ABC):
    time: float
    is_master: bool

    def __init__(self, node_id: int):
        self.quorum = None
        self.id = node_id
        self.is_candidate = False

        self.term = 0
        self.votes = 0
        self.vote_responses = 0
        # уникальный набор идентификаторов узлов, подтвердивших лидерство текущего узла
        self.granted = set()

        self.timeout = None
        self.heartbeat_timer = Timer(Config.heartbeat_interval, self.heartbeat)
        self.election_timer = Timer(self.election_interval, self.election_timeout)

    async def run(self):
        if self.is_master:
            print("{} become LEADER".format(self.id))
            print(self.quorum.state())
            self.heartbeat()
            self.heartbeat_timer.start()
        elif not self.is_candidate:
            self.election_timer.reset()
        await asyncio.sleep(3)

    def stop(self):
        self.heartbeat_timer.stop()
        self.election_timer.stop()

    def get_id(self):
        return self.id

    def is_master(self):
        return self.is_master

    def is_online(self):
        return self.is_online

    @staticmethod
    def election_interval():
        return random.uniform(Config.heartbeat_interval, Config.election_interval)

    def set_cluster_conf(self, quorum):
        self.quorum = quorum
        self.timeout = random.uniform(0, self.quorum.config.max_timeout)
        if self.is_master:
            self.quorum.master_id = self.id

    async def leader_election(self):
        self.election_timer.reset()
        self.vote_responses = 0
        print("{} become candidate".format(self.id))
        await self.send_vote_requests()

    def heartbeat(self):
        print("heartbeat")
        asyncio.ensure_future(self.send_append_entity_requests())

    def election_timeout(self):
        # если большинство узлов недоступно
        if self.is_candidate and \
                self.vote_responses + 1 < self.quorum.consensus_number:
            print("{} don't see consensus quorum".format(self.id))
        asyncio.ensure_future(self.leader_election())

    async def send_append_entity_requests(self):
        requests = []
        for i, (node_id, node) in enumerate(self.quorum.nodes.items()):
            if node_id == self.id:
                continue
            requests.append(self.send_append_entity_request(node_id))
        await asyncio.wait(requests)

    async def send_vote_requests(self):
        print("send vote requests")
        self.time = time.time()
        self.is_candidate = True
        # новый виток выборов
        self.term += 1
        self.votes = 1
        print(self.quorum.state())
        requests = []
        for i, (node_id, node) in enumerate(self.quorum.nodes.items()):
            if self.id == node_id:
                continue
            requests.append(asyncio.create_task(self.send_vote_request(node_id)))
        await asyncio.wait(requests)

    @abstractmethod
    async def send_append_entity_request(self, node_id: int):
        pass

    @abstractmethod
    async def send_vote_request(self, node_id: int):
        pass

    async def response(self, request: Request) -> Response:
        if request.get_term() >= self.term:
            if request.type is Request.RequestType.RequestVote:
                return await self.vote_response(request)
            elif request.type is Request.RequestType.AppendEntity:
                return await self.append_entity_response(request)
        else:
            return Response(self.id, self.term, False, request.type.name)

    async def append_entity_response(self, request: Request) -> Response:
        self.is_candidate = False
        self.is_master = False
        self.heartbeat_timer.stop()
        self.election_timer.reset()
        self.term = request.get_term()
        print("{} got append entity from {} and reset timer".format(self.id, request.id))
        return Response(self.id, self.term, True, request.type.name)

    async def vote_response(self, request: Request) -> Response:
        if request.get_term() > self.term:
            self.is_candidate = False
            self.is_master = False
            print("{} gave vote for {}".format(self.id, request.id))
            self.term = request.get_term()
            return Response(self.id, self.term, True, request.type.name)
        else:
            print("my term = {}, requests = {}".format(self.term, request.term))
            return Response(self.id, self.term, False, request.type.name)

    async def on_vote_response(self, response: Response):
        if not self.is_master:
            self.votes += response.is_success()
            self.vote_responses += 1
            print("{} on vote response from {}".format(self.id, response.id))
            if response.get_term() > self.term or \
                    (self.quorum.nodes[response.get_id()].is_master and response.get_term() == self.term):
                self.is_candidate = False
                self.votes = 0

            if self.votes >= self.quorum.consensus_number:
                self.is_master = True
                self.election_timer.stop()
                self.granted.clear()
                self.granted.add(self.id)
                # сразу запускаем лидера без подтверждения, а по необходимости останавливаем
                await self.run()

    async def on_append_entity_response(self, response: Response):
        # оставляем нового лидера также в роли кандидата пока он не получит признание от всех работающих нод
        # сразу запускаем лидера без подтверждения, а по необходимости останавливаем
        if self.is_candidate and not response.is_success():
            self.is_master = False
            self.is_candidate = False
            self.heartbeat_timer.stop()
            self.term = response.get_term()
            await self.run()
        else:
            if response.is_success():
                self.granted.add(response.id)

            # признание текущего узла как лидера
            if len(self.granted) >= self.quorum.consensus_number:
                self.is_candidate = False
                self.quorum.master_id = self.id
