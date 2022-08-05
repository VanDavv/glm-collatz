import argparse
import os
from datetime import timedelta

os.environ["YAGNA_APPKEY"] = "55359a3e7afb4525be26fff47accc41f"
import asyncio
import logging
import pathlib
from typing import AsyncIterable

from aiohttp import ClientConnectorError
from yapapi import Golem, Task, WorkContext, NoPaymentAccountError
from yapapi.log import enable_default_logger
from yapapi.payload import vm

log = logging.getLogger(__name__)


async def worker(context: WorkContext, tasks: AsyncIterable[Task]):
    async for task in tasks:
        script_dir = pathlib.Path(__file__).resolve().parent
        script = context.new_script(timeout=timedelta(minutes=10))
        script.upload_file(str(script_dir / "task.py"), "/golem/output/task.py")
        future_result = script.run("/usr/bin/python3", "/golem/output/task.py", str(task.data[0]), str(task.data[1]))
        yield script
        task.accept_result(result=await future_result)


def prepare_tasks(args):
    range_len = args.range_end - args.range_start
    batch_count = min(range_len, args.batch_size)
    if args.debug:
        print(f"Splitting range [{args.range_start} - {args.range_end}] into {batch_count} batches...")
    split_points = [args.range_start + round((range_len / batch_count) * i) for i in range(1, batch_count + 1)]
    batches = [(args.range_start if index == 0 else split_points[index - 1], split_point) for index, split_point in enumerate(split_points)]
    tasks = []
    for index, (start, end) in enumerate(batches):
        if args.debug:
            print(f"Batch #{index + 1}: {start} - {end}")
        tasks.append(Task(data=[start, end]))
    return tasks


async def main(args):
    package = await vm.repo(
        image_hash="9a3b5d67b0b27746283cb5f287c13eab1beaa12d92a9f536b747c7ae",
    )

    tasks = prepare_tasks(args)

    try:
        async with Golem(budget=1.0, subnet_tag="devnet-beta") as golem:
            async for completed in golem.execute_tasks(worker, tasks, payload=package):
                print(completed.result.stdout)
    except NoPaymentAccountError as ex:
        log.error(f"Sender is not initialized!\nPlease run \"yagna payment init --sender\" or consult the docs\nError: {ex}")
    except (ConnectionResetError, ClientConnectorError) as ex:
        log.error(f"Yagna client is not running!\nPlease run \"yagna service run\" or consult the docs\nError: {ex}")


if __name__ == "__main__":
    enable_default_logger(log_file="hello.log")
    parser = argparse.ArgumentParser()
    parser.add_argument("range_start", type=int, help="Specify search range start (inclusive)")
    parser.add_argument("range_end", type=int, help="Specify search range end, (non-inclusive)")
    parser.add_argument("-bs", "--batch-size", type=int, default=6, help="Specify on how many batches should the calculations be split")
    parser.add_argument("--debug", action="store_true", help="Enable debug logs")
    args = parser.parse_args()

    if not args.range_start < args.range_end:
        raise ValueError(f"Range start should be lower than range end! Received range {args.range_start} - {args.range_end}")

    loop = asyncio.get_event_loop()
    task = loop.create_task(main(args))
    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        pass
