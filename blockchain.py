import hashlib, json, time

def hash_block(block):
    data=json.dumps(block,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(data).hexdigest()

class Chain:
    def __init__(self):
        self.blocks=[{"index":0,"timestamp":0,"asset":"GENESIS","owner":"-","previous_hash":"0","hash":""}]
        self.blocks[0]["hash"]=hash_block(self.blocks[0])
    def add(self,asset,owner):
        prev=self.blocks[-1]["hash"]
        b={"index":len(self.blocks),"timestamp":time.time(),"asset":asset,"owner":owner,"previous_hash":prev}
        b["hash"]=hash_block(b); self.blocks.append(b)
    def valid(self):
        for i,b in enumerate(self.blocks):
            copy=dict(b); saved=copy.pop("hash")
            if hash_block(copy)!=saved: return False
            if i and b["previous_hash"]!=self.blocks[i-1]["hash"]: return False
        return True
