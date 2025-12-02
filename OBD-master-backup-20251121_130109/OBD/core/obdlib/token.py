import hashlib
from decouple import config


class HashObd:
    boa = config('HASH_OBDK1')
    boa2 = config('HASH_OBDK2')
    boa3 = config('HASH_OBDK3')

    def __init__(self, userEmail, username, first_name):
        self.email = str(userEmail).lower()
        self.username = str(username).lower()
        self.fisrt_name = str(first_name).lower()
        self.lenFirst = str(len(self.fisrt_name))
        self.md = (self.boa + self.email + self.boa2 + self.lenFirst + self.boa3 + self.username).encode("utf-8")
        self.digit = (self.lenFirst + self.boa + self.username + self.boa2 + self.fisrt_name).encode("utf-8")
        self.pin = ''

    def encript(self):
        mdhash = str(int(hashlib.md5(self.md).hexdigest(), 32))[::-1][::3][::-1][-6:]
        digit = str(int(hashlib.md5(self.digit).hexdigest(), 32))[::-1][::2][7]
        self.pin = mdhash + '-' + digit
        return self.pin

    def has_pin(self, pin_number):
        pin = self.encript()
        if not pin_number == pin:
            return bool(False)
        else:
            return bool(True)

