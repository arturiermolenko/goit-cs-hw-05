import argparse
import logging
from pathlib import Path
from aiofiles import os as async_os
from aiofiles import open as async_open
from asyncio import run

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Async file sorting")
    parser.add_argument("source", type=str, help="Path to source folder")
    parser.add_argument("output", type=str, help="Path to destination folder")
    return parser.parse_args()


async def read_folder(path: Path, output: Path) -> None:
    entries = await async_os.scandir(path)
    for entry in entries:
        if await async_os.path.isdir(entry.path):
            await read_folder(Path(entry.path), output)
        elif await async_os.path.isfile(entry.path):
            await copy_file(Path(entry.path), output)


async def copy_file(file: Path, output: Path) -> None:
    extension_name = file.suffix[1:] if file.suffix else "no_extension"
    extension_folder = output / extension_name

    await async_os.makedirs(extension_folder, exist_ok=True)

    destination = extension_folder / file.name
    async with async_open(file, "rb") as src, async_open(destination, "wb") as dest:
        await dest.write(await src.read())

    logging.info(f"File {file} is copied to {destination}")


if __name__ == "__main__":
    args = parse_arguments()
    source = Path(args.source)
    output = Path(args.output)

    if not source.exists():
        logging.error(f"Folder {source} does not exist")
        exit(1)

    output.mkdir(parents=True, exist_ok=True)

    run(read_folder(source, output))
