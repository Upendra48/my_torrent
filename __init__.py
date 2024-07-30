import asyncio
import sys

from download_session import download

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_torrent_file>")
        sys.exit(1)

    torrent_file = sys.argv[1]
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(download(torrent_file, '.', loop=loop))
    finally:
        loop.close()
