import zlib

data = "Hello, World!" * 100
checksum = zlib.crc32(data)

compressed = zlib.compress(data)
decompressed = zlib.decompress(compressed)

print(zlib.crc32(decompressed) == checksum)
