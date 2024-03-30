import zlib


def deflate(data: str) -> bytes:
    compress = zlib.compressobj(
        9, zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, 0
    )
    return compress.compress(data.encode("utf-8")) + compress.flush()


def inflate(data: bytes) -> str:
    decompress = zlib.decompressobj(-zlib.MAX_WBITS)
    return (decompress.decompress(data) + decompress.flush()).decode("utf-8")
