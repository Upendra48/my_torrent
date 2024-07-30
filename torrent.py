import copy
import hashlib
from pprint import pformat
import bencodepy as bencoder

class Torrent:
    def __init__(self, path: str):
        self.path = path
        self.info = self.read_torrent_file(path)
        if not self.info:
            raise ValueError(f"Failed to read torrent file: {path}")

    def __getitem__(self, item):
        return self.info.get(item, None)

    def get_piece_hash(self, piece_idx):
        pieces = self.info.get(b'info', {}).get(b'pieces', b'')
        start_idx = piece_idx * 20
        end_idx = (piece_idx * 20) + 20
        return pieces[start_idx:end_idx]

    @property
    def announce_url(self) -> str:
        return self.info.get(b'announce', b'').decode('utf-8')

    @property
    def info_hash(self):
        info_dict = self.info.get(b'info', {})
        if not info_dict:
            raise ValueError("No 'info' dictionary found in torrent file.")
        return hashlib.sha1(
            bencoder.encode(info_dict)
        ).digest()

    @property
    def size(self):
        info = self.info.get(b'info', {})
        if b'length' in info:
            return int(info[b'length'])
        elif b'files' in info:
            return sum(int(f.get(b'length', 0)) for f in info.get(b'files', []))
        else:
            raise ValueError("Torrent file does not contain 'length' or 'files'.")

    def read_torrent_file(self, path: str) -> dict:
        try:
            with open(path, 'rb') as f:
                return bencoder.decode(f.read())
        except (FileNotFoundError, bencoder.BencodeDecodeError) as e:
            print(f"Error reading torrent file {path}: {e}")
            return {}

    def __str__(self):
        info = copy.deepcopy(self.info)
        if b'info' in info:
            del info[b'info'][b'pieces']
        return pformat(info)
