import asyncio
import time

from rafty import FakeQuorum, FakeNode


async def main(loop):
    cluster = FakeQuorum([FakeNode(1, True), FakeNode(2), FakeNode(3)], loop=loop)
    t_start = time.time()
    print(cluster.state())
    # while True:
    #     if time.time() > t_start + 40:
    #         print(cluster.state())
    #         break
    #     elif time.time() > t_start + 30:
    #         await cluster.set_offline(cluster.get_master())
    #         print(cluster.state())
    #     elif time.time() > t_start + 20:
    #         await cluster.set_online(1)
    #         print(cluster.state())
    #     elif time.time() > t_start + 1:
    #         await cluster.set_offline(1)
    #         print(cluster.state())
    await cluster.set_offline(1)
    print("Отключаем ноду 1")
    print(cluster.state())
    await cluster.set_online(1)
    print("Включаем ноду 1")
    print(cluster.state())
    await cluster.set_offline(cluster.get_master())
    print("Отключаем мастера")
    print(cluster.state())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
