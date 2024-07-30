import asyncio
import hashlib
import math
from typing import Dict, List
from pprint import pformat

from file_saver import FileSaver
from peer import Peer
from torrent import Torrent
from util import LOG, REQUEST_SIZE

class Piece(object):
    def __init__(self, index: int, blocks: list):
        self.index: int = index
        self.blocks: list = blocks
        self.downloaded_blocks = [False] * len(blocks)

    def flush(self):
        for block in self.blocks:
            block.flush()

    def is_complete(self) -> bool:
        return all(self.downloaded_blocks)

    def save_block(self, begin: int, data: bytes):
        for block_idx, block in enumerate(self.blocks):
            if block.begin == begin:
                block.data = data
                self.downloaded_blocks[block_idx] = True

    @property
    def data(self) -> bytes:
        return b''.join([block.data for block in self.blocks])

    @property
    def hash(self):
        return hashlib.sha1(self.data).digest()

    def __repr__(self):
        return '<Piece: {} Blocks: {}>'.format(self.index, len(self.blocks))


class Block(object):
    def __init__(self, piece, begin, length):
        self.piece = piece
        self.begin = begin
        self.length = length
        self.data = None

    def flush(self):
        self.data = None

    def __repr__(self):
        return '[Block ({}, {}, {})]'.format(self.piece, self.begin, self.length)


class DownloadSession(object):
    def __init__(self, torrent: Torrent, received_blocks: asyncio.Queue = None):
        self.torrent: Torrent = torrent
        self.piece_size: int = self.torrent[b'info'][b'piece length']
        self.number_of_pieces: int = math.ceil(self.torrent.size / self.piece_size)
        self.pieces: List[Piece] = self.get_pieces()
        self.pieces_in_progress: Dict[int, Piece] = {}
        self.received_pieces: Dict[int, Piece] = {}
        self.received_blocks: asyncio.Queue = received_blocks

    def on_block_received(self, piece_idx, begin, data):
        piece = self.pieces[piece_idx]
        piece.save_block(begin, data)

        if not piece.is_complete():
            return

        piece_data = piece.data

        res_hash = hashlib.sha1(piece_data).digest()
        exp_hash = self.torrent.get_piece_hash(piece.index)

        if res_hash != exp_hash:
            LOG.info('Hash check failed for Piece {}'.format(piece.index))
            piece.flush()
            return
        else:
            LOG.info('Piece {} hash is valid'.format(piece.index))

        self.received_blocks.put_nowait((piece.index * self.piece_size, piece_data))
        self.received_pieces[piece.index] = piece
        del self.pieces_in_progress[piece.index]

    def get_pieces(self) -> List[Piece]:
        pieces = []
        blocks_per_piece = math.ceil(self.piece_size / REQUEST_SIZE)
        for piece_idx in range(self.number_of_pieces):
            blocks = []
            for block_idx in range(blocks_per_piece):
                is_last_block = (blocks_per_piece - 1) == block_idx
                block_length = (
                    (self.piece_size % REQUEST_SIZE) or REQUEST_SIZE
                    if is_last_block
                    else REQUEST_SIZE
                )
                blocks.append(
                    Block(
                        piece_idx,
                        block_length * block_idx,
                        block_length
                    )
                )
            pieces.append(Piece(piece_idx, blocks))
        return pieces

    def get_piece_request(self, have_pieces):
        for piece in self.pieces:
            is_piece_downloaded = piece.index in self.received_pieces
            is_piece_in_progress = piece.index in self.pieces_in_progress

            if is_piece_downloaded or is_piece_in_progress:
                continue

            if have_pieces[piece.index]:
                self.pieces_in_progress[piece.index] = piece
                return piece
        raise Exception('No eligible pieces to request')

    def __repr__(self):
        data = {
            'number of pieces': self.number_of_pieces,
            'piece size': self.piece_size,
            'pieces': self.pieces[:5]
        }
        return pformat(data)
