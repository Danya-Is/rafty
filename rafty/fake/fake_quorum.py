from rafty import FakeNode, AbstractQuorum
from typing import List


class FakeQuorum(AbstractQuorum):

    def __init__(self, nodes: List[FakeNode], loop):
        super().__init__(nodes, loop)

    # контролируем выведение нод из строя, в рабочем варианте мастер посылает всем фолловерам пинг
    async def set_offline(self, node_id):
        self.online_nodes_amount -= 1
        await self.nodes[node_id].set_offline()

    async def set_online(self, node_id):
        self.online_nodes_amount += 1
        self.nodes[node_id].set_online()


