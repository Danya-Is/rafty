import asyncio
import time

from rafty import FakeNode
from rafty import FakeQuorum


async def main(loop):
    cluster = FakeQuorum([FakeNode(1, is_master=True, is_owner=True), FakeNode(2), FakeNode(3)], loop=loop)
    await cluster.run()
    t_start = time.time()
    # print(cluster.state())

    while True:
        if time.time() > t_start + 40:
            # print(cluster.state())
            break
        elif time.time() > t_start + 30:
            await cluster.set_offline(cluster.get_master())
            # print(cluster.state())
        elif time.time() > t_start + 20:
            await cluster.set_online(1)
            # print(cluster.state())
        elif time.time() > t_start + 10:
            await cluster.set_offline(1)
            # print(cluster.state())

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(main(loop))
