class StreamIterator:
    async def __anext__(self):
        raise StopAsyncIteration
