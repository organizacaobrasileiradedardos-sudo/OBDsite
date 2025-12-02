from datetime import date
from decouple import config
from obd.core.obdlib.token import HashObd


class ObdSession:

    def __init__(self):
        self.hash = ''

    def __str__(self):
        return self.hash

    def startSession(self):
        self.hash = str(HashObd(config('HASH_OBDK1'), date.today(), config('HASH_OBDK2')).encript())
        return str(self.hash)

    def validate_token(self, from_user_session):
        if from_user_session == self.get_token():
            return True
        else:
            return False

    @property
    def get_token(self):
        hash = str(HashObd(config('HASH_OBDK1'), date.today(), config('HASH_OBDK2')).encript())
        return hash
