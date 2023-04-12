import asyncio

DEBOUNCE_TASKS = {}
THROTTLE_VALS = {}
THROTTLE_TASKS = {}


def debounced_run(callback, args=[], delay=0):
    func_name = callback.__qualname__
    if func_name in DEBOUNCE_TASKS:
        DEBOUNCE_TASKS[func_name].cancel()

    async def task():
        await asyncio.sleep(delay)
        callback(*args)
        del DEBOUNCE_TASKS[func_name]

    DEBOUNCE_TASKS[func_name] = asyncio.create_task(task())


def throttled_run(callback, args=[], rate=float("inf")):
    func_name = callback.__qualname__

    THROTTLE_VALS[func_name] = args

    throttle_task = THROTTLE_TASKS.get(func_name, None)
    if throttle_task is not None and not throttle_task.done():
        return

    async def task():
        while THROTTLE_VALS.get(func_name, None):
            args = THROTTLE_VALS[func_name]
            del THROTTLE_VALS[func_name]
            callback(*args)
            await asyncio.sleep(1 / rate)

    THROTTLE_TASKS[func_name] = asyncio.create_task(task())
