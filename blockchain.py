
import hashlib
import json
import time


def hash_block(block):
    data = json.dumps(
        block,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")

    return hashlib.sha256(data).hexdigest()


class Chain:

    def __init__(self):
        self.blocks = [
            {
                "index": 0,
                "timestamp": 0,
                "asset": "GENESIS",
                "owner": "-",
                "previous_hash": "0",
                "hash": ""
            }
        ]

        self.blocks[0]["hash"] = hash_block(
            {
                k: v
                for k, v in self.blocks[0].items()
                if k != "hash"
            }
        )

    def add(self, asset, owner):
        if not asset or not owner:
            raise ValueError(
                "Nama aset dan pemilik wajib diisi."
            )

        previous = self.blocks[-1]["hash"]

        block = {
            "index": len(self.blocks),
            "timestamp": time.time(),
            "asset": asset,
            "owner": owner,
            "previous_hash": previous
        }

        block["hash"] = hash_block(block)

        self.blocks.append(block)

    def valid(self):

        if not self.blocks:
            return False

        for i, block in enumerate(self.blocks):

            copy = dict(block)
            saved_hash = copy.pop("hash", None)

            if hash_block(copy) != saved_hash:
                return False

            if i == 0:
                if block["previous_hash"] != "0":
                    return False

                if block["index"] != 0:
                    return False

            else:
                previous = self.blocks[i - 1]

                if block["previous_hash"] != previous["hash"]:
                    return False

                if block["index"] != i:
                    return False

        return True
