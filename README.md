# Torrent Client

This is a simple torrent client written in Python. The client is capable of decoding torrent files, interacting with a tracker, and downloading pieces of a file from peers.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/my_torrent.git
    ```
2. Change into the project directory:
    ```bash
    cd my_torrent
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The client can be run with different commands for various functionalities.

### Commands

- `decode`: Decodes a bencoded value.
    ```bash
    python main.py decode <bencoded_value>
    ```

- `info`: Prints the torrent file information.
    ```bash
    python main.py info <filename>
    ```

- `peers`: Retrieves and prints the list of peers from the tracker.
    ```bash
    python main.py peers <filename>
    ```

- `handshake`: Initiates a handshake with a specified peer.
    ```bash
    python main.py handshake <filename> <peer_ip>:<peer_port>
    ```

- `download_piece`: Downloads a specific piece of the torrent file.
    ```bash
    python main.py download_piece -o <outputfile> <filename> <piececount>
    ```

- `download`: Downloads the entire torrent file.
    ```bash
    python main.py download -o <outputfile> <filename>
    ```

## Code Overview

### Main Components

1. **Decoding and Encoding Bencoded Data**

    Functions for decoding and encoding bencoded data, which is the format used in torrent files.
    
    ```python
    def decode_bencode(bencoded_value):
        # Implementation here
    ```

2. **Torrent File Handling**

    Functions for decoding a torrent file and extracting information.
    
    ```python
    def decode_torrentfile(filename):
        # Implementation here
    ```

3. **Tracker Interaction**

    Function to get the list of peers from the tracker.
    
    ```python
    def get_peers(filename):
        # Implementation here
    ```

4. **Peer Interaction**

    Functions for initiating a handshake and communicating with peers.
    
    ```python
    def init_handshake(filename, peer):
        # Implementation here
    ```

5. **Piece and Block Management**

    Classes for managing the downloading of pieces and blocks.
    
    ```python
    class Piece:
        def __init__(self, index, blocks):
            # Implementation here
    ```

    ```python
    class Block:
        def __init__(self, piece, begin, length):
            # Implementation here
    ```

6. **Download Session**

    Class for managing the download session, including handling blocks received from peers.
    
    ```python
    class DownloadSession:
        def __init__(self, torrent, received_blocks):
            # Implementation here
    ```

7. **Logger Setup**

    Basic logging setup for the client.
    
    ```python
    import logging
    LOG = logging.getLogger('torrent_client')
    ```

8. **Constants and Peer ID Generation**

    Constant definitions and peer ID generation.
    
    ```python
    REQUEST_SIZE = 2**14  # 16KB per block

    def generate_peer_id():
        # Implementation here
    ```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
