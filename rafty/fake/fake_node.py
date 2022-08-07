import asyncio

from rafty import Request, AbstractNode


class FakeNode(AbstractNode):

    def __init__(self, node_id: int, is_master=False, is_owner=False):
        super().__init__(node_id)
        self.is_master = is_master
        self.is_owner = is_owner
        self.is_online = True

    async def set_offline(self):
        if self.is_online:
            self.is_online = False
            self.log.info("{} offline".format(self.id))
            if self.is_master:
                self.is_master = False
                self.heartbeat_timer.stop()
            else:
                self.election_timer.stop()
        await asyncio.sleep(3)

    # поле is_online сейчас используется только для симуляции сетевого взаимодействия,
    # тк в рабочем состоянии рафт продолжает посылку сообщений даже недостопным узлам
    def set_online(self):
        if not self.is_online:
            self.is_online = True
            asyncio.ensure_future(self.run())

    async def send_vote_request(self, node_id: int):
        if self.quorum.nodes[node_id].is_online:
            await self.on_vote_response(await self.quorum.nodes[node_id].response(Request(self.id, self.term, 'RequestVote')))

    async def send_append_entity_request(self, node_id: int):
        if self.quorum.nodes[node_id].is_online:
            await self.on_append_entity_response(await self.quorum.nodes[node_id].response(Request(self.id, self.term, 'AppendEntity')))
