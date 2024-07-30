import asyncio
import struct
from collections import defaultdict

import bitstring
from util import LOG, PEER_ID, REQUEST_SIZE

class Peer(object):
    def __init__(self, torrent_session, host, port):
        self.host = host
        self.port = port
        self.torrent_session = torrent_session

        self.have_pieces = bitstring.BitArray(
            bin='0' * self.torrent_session.number_of_pieces
        )
        self.piece_in_progress = None
        self.blocks = None

        self.inflight_requests = 0

    def handshake(self):
        return struct.pack(
            '>B19s8x20s20s',
            19,
            b'BitTorrent protocol',
            self.torrent_session.torrent.info_hash,
            PEER_ID.encode()
        )

    async def send_interested(self, writer):
        msg = struct.pack('>Ib', 1, 2)
        writer.write(msg)
        await writer.drain()

    def get_blocks_generator(self):
        def blocks():
            while True:
                piece = self.torrent_session.get_piece_request(self.have_pieces)
                LOG.info('[{}] Generating blocks for Piece: {}'.format(self, piece))
                for block in piece.blocks:
                    yield block
        if not self.blocks:
            self.blocks = blocks()
        return self.blocks

    async def request_a_piece(self, writer):
        if self.inflight_requests > 1:
            return
        blocks_generator = self.get_blocks_generator()
        block = next(blocks_generator)

        LOG.info('[{}] Request Block: {}'.format(self, block))
        msg = struct.pack('>IbIII', 13, 6, block.piece, block.begin, block.length)
        writer.write(msg)
        self.inflight_requests += 1
        await writer.drain()

    async def download(self):
        retries = 0
        while retries < 5:
            retries += 1
            try:
                await self._download()
            except asyncio.TimeoutError:
                LOG.warning('Timed out connecting with: {}'.format(self.host))

    async def _download(self):
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=10
            )
        except ConnectionError:
            LOG.error('Failed to connect to Peer {}'.format(self))
            return

        LOG.info('{} Sending handshake'.format(self))
        writer.write(self.handshake())
        await writer.drain()

        handshake = await reader.read(68)

        await self.send_interested(writer)

        buf = b''
        while True:
            resp = await reader.read(REQUEST_SIZE)

            buf += resp

            if not buf and not resp:
                return

            while True:
                if len(buf) < 4:
                    break

                length = struct.unpack('>I', buf[0:4])[0]

                if not len(buf) >= length:
                    break

                def consume(buf):
                    buf = buf[4 + length:]
                    return buf

                def get_data(buf):
                    return buf[:4 + length]

                if length == 0:
                    LOG.info('[Message] Keep Alive')
                    buf = consume(buf)
                    data = get_data(buf)
                    LOG.info('[DATA]', data)
                    continue

                if len(buf) < 5:
                    break

                msg_id = struct.unpack('>b', buf[4:5])[0]

                if msg_id == 0:
                    LOG.info('[Message] CHOKE')
                    data = get_data(buf)
                    buf = consume(buf)
                    LOG.info('[DATA]', data)

                elif msg_id == 1:
                    data = get_data(buf)
                    buf = consume(buf)
                    LOG.info('[Message] UNCHOKE')
                    self.peer_choke = False

                elif msg_id == 2:
                    data = get_data(buf)
                    buf = consume(buf)
                    LOG.info('[Message] Interested')
                    pass

                elif msg_id == 3:
                    data = get_data(buf)
                    buf = consume(buf)
                    LOG.info('[Message] Not Interested')
                    pass

                elif msg_id == 4:
                    buf = buf[5:]
                    data = get_data(buf)
                    buf = consume(buf)
                    LOG.info('[Message] Have')
                    pass

                elif msg_id == 5:
                    bitfield = buf[5: 5 + length - 1]
                    self.have_pieces = bitstring.BitArray(bitfield)
                    LOG.info('[Message] Bitfield: {}'.format(bitfield))

                    buf = buf[4 + length:]
                    await self.send_interested(writer)

                elif msg_id == 7:
                    self.inflight_requests -= 1
                    data = get_data(buf)
                    buf = consume(buf)

                    l = struct.unpack('>I', data[:4])[0]
                    try:
                        parts = struct.unpack(
                            '>IbII' + str(l - 9) + 's',
                            data[:length + 4])
                        piece_idx, begin, data = parts[2], parts[3], parts[4]
                        self.torrent_session.on_block_received(piece_idx, begin, data)
                    except struct.error:
                        LOG.info('error decoding piece')
                        return None

                else:
                    LOG.info('unknown ID {}'.format(msg_id))

                await self.request_a_piece(writer)

    def __repr__(self):
        return '[Peer {}:{}]'.format(self.host, self.port)
