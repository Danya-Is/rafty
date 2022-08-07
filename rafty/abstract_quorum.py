import asyncio
import logging
from abc import ABC
from typing import List

from rafty import AbstractNode, Config


class AbstractQuorum(ABC):
    nodes: dict
    online_nodes_amount: int
    consensus_number: int
    master_id: int
    loop = None

    def __init__(self, nodes: List[AbstractNode], loop):
        self.nodes = {node.get_id(): node for _, node in enumerate(nodes)}
        self.online_nodes_amount = len(nodes)
        self.consensus_number = self.online_nodes_amount // 2 + 1
        self.loop = loop
        self.config = Config()

        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

        for i, (node_id, node) in enumerate(self.nodes.items()):
            self.nodes[node_id].set_cluster_conf(self)

    async def run(self):
        tasks = []
        for i, (node_id, node) in enumerate(self.nodes.items()):
            tasks.append(asyncio.create_task(node.run()))
        await asyncio.wait(tasks)

    def stop(self):
        for i, (node_id, node) in enumerate(self.nodes.items()):
            node.stop()

    def get_master(self) -> int:
        return self.master_id

    # TODO информация в нормальном формате
    def state(self) -> str:
        res = "Quorum( "
        for i, (node_id, node) in enumerate(self.nodes.items()):
            if node.is_master:
                role = "master"
            elif node.is_candidate:
                role = "candidate"
            else:
                role = "follower"
            str = "Node(id={id}, is_online={is_online}, status={status}, term={term}) "\
                .format(id=node_id, is_online=node.is_online, status=role, term=node.term)
            res += str

        res += ")"
        return res
