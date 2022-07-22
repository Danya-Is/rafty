from abc import ABC
from typing import List

from rafty import AbstractNode


class AbstractQuorum(ABC):
    nodes: dict
    online_nodes_amount: int
    consensus_number: int
    master_id: int
    loop = None

    def __init__(self, nodes: List[AbstractNode], loop):
        self.nodes = {node.get_id(): node for _, node in enumerate(nodes)}
        self.online_nodes_amount = len(nodes)
        for i, (node_id, node) in enumerate(self.nodes.items()):
            self.nodes[node_id].set_cluster_conf(self)
        self.consensus_number = self.online_nodes_amount // 2 + 1
        self.loop = loop

    def get_master(self) -> int:
        return self.master_id

    # TODO информация в нормальном формате
    def state(self) -> str:
        res = "Quorum( "
        for i, (node_id, node) in enumerate(self.nodes.items()):
            str = "Node(id={id}, is_online={is_online}, is_master={is_master}) "\
                .format(id=node_id, is_online=node.is_online, is_master=node.is_master)
            res += str

        res += ")"
        return res
