import ipaddress
import socket
import struct
import urllib.parse as urlparse

import aiohttp  
import bencodepy as bencoder

from util import LOG, PEER_ID


class Tracker(object):
    def __init__(self, torrent):
        self.torrent = torrent
        self.tracker_url = torrent.announce_url
        self.peers = []

    async def get_peers(self):
        peers_resp = await self.request_peers()
        if b'failure reason' in peers_resp:
            LOG.error(f"Tracker error: {peers_resp[b'failure reason'].decode('utf-8')}")
            raise RuntimeError('Failed to get Peers from Tracker')
        if b'peers' not in peers_resp:
            LOG.error('No peers found in tracker response')
            raise RuntimeError('No peers found in Tracker response')
        peers = self.parse_peers(peers_resp[b'peers'])
        return peers

    async def request_peers(self):
        async with aiohttp.ClientSession() as session:
            resp = await session.get(self.tracker_url, params=self._get_request_params())
            resp_data = await resp.read()
            LOG.info('Tracker response: {}'.format(resp))
            LOG.info('Tracker response data: {}'.format(resp_data))
            peers = None
            try:
                peers = bencoder.decode(resp_data)
                LOG.info('Tracker response data bdecoded: {}'.format(peers))
            except AssertionError:
                LOG.error('Failed to decode Tracker response: {}'.format(resp_data))
                LOG.error('Tracker request URL: {}'.format(str(resp.url).split('&')))
                raise RuntimeError('Failed to get Peers from Tracker')
            return peers

    def _get_request_params(self):
        # Ensure info_hash is a string of hex digits
        info_hash_hex = self.torrent.info_hash.hex()
        info_hash_bytes = bytes.fromhex(info_hash_hex)
        encoded_info_hash = urlparse.quote_from_bytes(info_hash_bytes)
        LOG.info('Encoded info_hash: {}'.format(encoded_info_hash))
        return {
            'info_hash': encoded_info_hash,
            'peer_id': PEER_ID,
            'compact': 1,
            'no_peer_id': 0,
            'event': 'started',
            'port': 59696,
            'uploaded': 0,
            'downloaded': 0,
            'left': self.torrent.size
        }

    def parse_peers(self, peers: bytes):
        self_addr = socket.gethostbyname(socket.gethostname())
        self_addr = '192.168.99.1'
        LOG.info('Self addr is: {}'.format(self_addr))

        def handle_bytes(peers_data):
            peers = []
            for i in range(0, len(peers_data), 6):
                addr_bytes, port_bytes = (
                    peers_data[i:i + 4], peers_data[i + 4:i + 6]
                )
                ip_addr = str(ipaddress.IPv4Address(addr_bytes))
                if ip_addr == self_addr:
                    LOG.info('Skipping self address: {}'.format(ip_addr))
                    continue
                port = struct.unpack('>H', port_bytes)[0]
                peers.append((ip_addr, port))
            return peers

        def handle_dict(peers):
            raise NotImplementedError

        handlers = {
            bytes: handle_bytes,
            dict: handle_dict
        }
        return handlers[type(peers)](peers)
