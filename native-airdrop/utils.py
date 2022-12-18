import bech32

def bech32encode(prefix, data):    
    return bech32.bech32_encode(prefix, bech32.convertbits(data, 8, 5, True))

def bech32decode(address):
    prefix, data = bech32.bech32_decode(address)        
    return prefix, bech32.convertbits(data, 5, 8, False)