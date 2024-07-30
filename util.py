import logging
import random
import string

# Logger setup
logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger('torrent_client')

# Constants
REQUEST_SIZE = 2**14  # 16KB per block

# Generate a peer ID similar to how BitTorrent does it
def generate_peer_id():
    return '-PC0001-' + ''.join(random.choices(string.ascii_letters + string.digits, k=12))

PEER_ID = generate_peer_id()
