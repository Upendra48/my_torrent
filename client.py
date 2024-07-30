import asyncio
import logging
import sys
from download_session import DownloadSession
from file_saver import FileSaver
from peer import Peer
from torrent import Torrent
from tracker import Tracker
from util import LOG, REQUEST_SIZE

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)7s: %(message)s',
    stream=sys.stderr,
)

async def download(torrent_file: str, download_location: str, loop=None):
    # Parse torrent file
    torrent = Torrent(torrent_file)
    LOG.info('Torrent: {}'.format(torrent))

    torrent_writer = FileSaver(download_location, torrent)
    session = DownloadSession(torrent, torrent_writer.get_received_blocks_queue())

    # Instantiate tracker object
    tracker = Tracker(torrent)

    peers_info = await tracker.get_peers()

    seen_peers = set()
    peers = [
        Peer(session, host, port)
        for host, port in peers_info
    ]
    seen_peers.update([str(p) for p in peers])

    LOG.info('[Peers] {}'.format(seen_peers))

    await (
        asyncio.gather(*[
            peer.download()
            for peer in peers
        ])
    )

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(download(sys.argv[1], '.', loop=loop))
    loop.close()
