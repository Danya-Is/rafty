from fake_node import FakeNode
from typing import List
import asyncio


class FakeQuorum:

    nodes: dict
    online_nodes_amount: int
    consensus_number: int
    loop = None

    def __init__(self, nodes: List[FakeNode], loop):
        self.nodes = {node.get_id() : node for _, node in enumerate(nodes)}
        self.online_nodes_amount = len(nodes)
        for i, (id, node) in enumerate(self.nodes.items()):
            self.nodes[id].set_cluster_conf(self)
        self.consensus_number = self.online_nodes_amount // 2 + 1
        self.loop = loop

    # контролируем выведение нод из строя, в рабочем варианте мастер посылает всем фолловерам пинг
    async def set_offline(self, node_id):
        self.nodes[node_id].set_offline()
        self.online_nodes_amount -= 1
        self.consensus_number = self.online_nodes_amount // 2 + 1
        if self.nodes[node_id].is_master:
            self.nodes[node_id].is_master = False
            await self.leader_election()

    async def set_online(self, node_id):
        self.online_nodes_amount += 1
        self.consensus_number = self.online_nodes_amount // 2 + 1
        self.nodes[node_id].set_online()

    # TODO обновлять информацию о текущем мастере по мере изменения состояния
    def get_master(self) -> int:
        for i, (node_id, node) in enumerate(self.nodes.items()):
            if node.is_master:
                return node_id
            
    async def leader_election(self):
        tasks = []
        for i, (node_id, node) in enumerate(self.nodes.items()):
            if node.is_online:
                await node.send_vote_requests()



    # TODO информация в нормальном формате
    def state(self) -> str:
        res = "Quorum( "
        for i, (node_id, node) in enumerate(self.nodes.items()):
            str = "Node(id={id}, is_online={is_online}, is_master={is_master}) "\
                .format(id=node_id, is_online=node.is_online, is_master=node.is_master)
            res += str

        res += ")"
        return res


