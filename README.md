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
    
## Tracker

The `Tracker` class handles communication with the tracker to retrieve the list of peers for the torrent.

### Methods

#### `__init__(self, torrent)`

Initializes the `Tracker` object with the given torrent.

- `torrent`: The torrent object containing the necessary torrent information.

#### `async get_peers(self)`

Fetches the list of peers from the tracker. Raises a `RuntimeError` if the tracker response contains an error or no peers.

- Returns: A list of peers.

#### `async request_peers(self)`

Sends a request to the tracker and returns the decoded response. Raises a `RuntimeError` if the response cannot be decoded.

- Returns: The decoded tracker response.

#### `_get_request_params(self)`

Generates the request parameters for the tracker request.

- Returns: A dictionary of request parameters.

#### `parse_peers(self, peers: bytes)`

Parses the peers from the tracker response. Supports compact peer format.

- `peers`: The peers data in bytes format.
- Returns: A list of peer tuples in the format `(ip_address, port)`.


## Torrent

The `Torrent` class is responsible for handling torrent file data, including reading the file, extracting relevant information, and providing access to specific properties such as the announce URL, info hash, and the size of the torrent.

### Methods

#### `__init__(self, path: str)`

Initializes the `Torrent` object with the path to the torrent file.

- `path`: The path to the torrent file.

#### `__getitem__(self, item)`

Allows dictionary-like access to the torrent's information dictionary.

- `item`: The key to access in the torrent's information dictionary.
- Returns: The value associated with the key, or `None` if the key is not found.

#### `get_piece_hash(self, piece_idx: int)`

Returns the SHA-1 hash of the specified piece.

- `piece_idx`: The index of the piece.
- Returns: The 20-byte hash of the piece.

### Properties

#### `announce_url`

Returns the announce URL for the torrent.

- Returns: The announce URL as a string.

#### `info_hash`

Returns the SHA-1 hash of the info dictionary.

- Returns: The SHA-1 hash of the info dictionary.

#### `size`

Calculates the total size of the torrent data.

- Returns: The size of the torrent data in bytes.
- Raises: `ValueError` if the torrent file does not contain `length` or `files` information.

### Helper Methods

#### `read_torrent_file(self, path: str)`

Reads and decodes the torrent file.

- `path`: The path to the torrent file.
- 'Returns : A dictionary representing the decoded torrent file.
- Prints an error message and returns an empty dictionary if the file cannot be read or decoded.


## Peer

The `Peer` class represents a peer in the BitTorrent network. It handles the connection to a peer, sending and receiving messages, and managing the download of pieces.

### Methods

#### `__init__(self, torrent_session, host, port)`

Initializes a `Peer` object with the given torrent session, host, and port.

- `torrent_session`: The torrent session to which this peer belongs.
- `host`: The IP address of the peer.
- `port`: The port number of the peer.

#### `handshake(self)`

Creates the handshake message to initiate communication with the peer.

- Returns: The handshake message as bytes.

#### `send_interested(self, writer)`

Sends an "interested" message to the peer.

- `writer`: The asyncio StreamWriter object used to send the message.
- Returns: None.

#### `get_blocks_generator(self)`

Returns a generator for requesting blocks.

- Returns: A generator that yields blocks to be requested.

#### `request_a_piece(self, writer)`

Requests a block from the peer if the number of in-flight requests is less than or equal to 1.

- `writer`: The asyncio StreamWriter object used to send the request.
- Returns: None.

#### `download(self)`

Attempts to download data from the peer, retrying up to 5 times in case of failure.

- Returns: None.

#### `_download(self)`

Handles the actual downloading process, including establishing the connection and managing communication with the peer.

- Returns: None.

## DownloadSession, Piece, and Block Classes

These classes handle the core logic of downloading and verifying pieces of a torrent.

### DownloadSession

Manages the state and progress of the torrent download.

#### Attributes

- `torrent`: An instance of the `Torrent` class containing torrent metadata.
- `piece_size`: The size of each piece as specified in the torrent file.
- `number_of_pieces`: The total number of pieces in the torrent.
- `pieces`: A list of `Piece` objects representing each piece of the torrent.
- `pieces_in_progress`: A dictionary of pieces currently being downloaded.
- `received_pieces`: A dictionary of pieces that have been fully downloaded and verified.
- `received_blocks`: An asyncio queue for storing downloaded blocks.

#### Methods

- `on_block_received(piece_idx, begin, data)`: Handles a newly received block of data.
- `get_pieces()`: Initializes and returns a list of `Piece` objects.
- `get_piece_request(have_pieces)`: Determines the next piece to request based on the available pieces.

### Piece

Represents a single piece of the torrent, containing multiple blocks.

#### Attributes

- index: The index of the piece.
- blocks: A list of Block objects that make up the piece.
- downloaded_blocks: A list indicating whether each block has been downloaded.

#### Methods

- flush(): Clears the data of all blocks in the piece.
- is_complete(): Checks if all blocks in the piece have been downloaded.
- save_block(begin, data): Saves a block of data to the piece.
- data: Concatenates and returns the data of all blocks in the piece.
- hash: Computes and returns the SHA-1 hash of the piece's data.

### Block

Represents a single block of data within a piece.

#### Attributes

- piece: The index of the piece the block belongs to.
- begin: The starting byte offset of the block within the piece.
- length: The length of the block.
- data: The data of the block.
#### Methods

- flush(): Clears the block's data.

## FileSaver Class

The `FileSaver` class is responsible for writing downloaded pieces to a file. It handles creating the file, managing the file descriptor, and writing blocks of data as they are received.

### Attributes

- `file_name`: The path to the file where the torrent data will be saved.
- `fd`: The file descriptor for the output file.
- `received_blocks_queue`: An asyncio queue for storing blocks of data to be written to the file.

### Methods

- `__init__(self, outdir, torrent)`: Initializes the `FileSaver` instance, creates the output file, and starts the asyncio task to process the received blocks.
- `get_received_blocks_queue()`: Returns the queue used to store received blocks of data.
- `get_file_path(self, outdir, torrent)`: Constructs the file path for the output file based on the torrent's name.


## Main Download Script

This script is the entry point for the torrent client. It handles the initialization of the torrent download process, including parsing the torrent file, setting up the session, and managing peers.

### Usage

To run the script, execute the following command in your terminal:

```bash
python main_script.py path_to_torrent_file.torrent
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.


