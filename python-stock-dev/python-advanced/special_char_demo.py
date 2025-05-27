import binascii


string = binascii.unhexlify(b'01000721303030373530')

with open('demo.txt', 'wb') as f:
    f.write(string)
