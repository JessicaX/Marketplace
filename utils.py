import hashlib

def md5_hash(value):
    return hashlib.md5((value + "carousell" + "cs6400").encode('utf-8')).hexdigest()