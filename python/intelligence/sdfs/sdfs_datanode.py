"""
[SOVEREIGN FORGE] Algorithmic Python Synthesis
"""
import os
import hashlib


class DataNode:
    def __init__(self, storage_dir: str):
        self.dir = storage_dir
        os.makedirs(self.dir, exist_ok=True)

    def store_chunk(self, chunk_id: str, data: bytes):
        hash_val = hashlib.sha256(data).hexdigest()
        with open(os.path.join(self.dir, chunk_id), 'wb') as f:
            f.write(data)
        print(f'Stored chunk {chunk_id} with hash {hash_val}')
        return hash_val



