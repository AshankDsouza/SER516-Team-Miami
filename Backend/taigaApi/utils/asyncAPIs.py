import asyncio
from aiohttp import ClientSession

async def execute_apis(url: str, queue: asyncio.Queue, headers):
    async with ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            result = await response.json()
            await queue.put(result)


async def build_and_execute_apis(params, api_url, headers):
    # I'm using test server localhost, but you can use any url
    results = []
    queue = asyncio.Queue()
    async with asyncio.TaskGroup() as group:
        for i in params:
            group.create_task(execute_apis(api_url+str(i), queue, headers))

    while not queue.empty():
        results+=await queue.get()


    return results

