import hashlib
import hmac
import os
from typing import Tuple


def hash_new_password(password: str) -> Tuple[bytes, bytes]:
    """
    Hash the provided password with a randomly-generated salt and return the
    salt and hash to store in the database.
    """

    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt, pw_hash


def is_correct_password(salt: bytes, pw_hash: bytes, password: str) -> bool:
    """
    Given a previously-stored salt and hash, and a password provided by a user
    trying to log in, check whether the password is correct.
    """

    return hmac.compare_digest(
        pw_hash,
        hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    )


def is_resource_open(resource: str) -> bool:
    return True


def is_key_valid(auth_key) -> bool:
    return False


def is_authorized(auth_key: str, topic_hierarchy: str) -> bool:
    # validate password
    if is_correct_password(salt, auth_key):
        return True
    return False


password = 'tomkralidis'
salt, pw_hash = hash_new_password(password)

print(salt)
print(pw_hash)

assert is_correct_password(salt, pw_hash, 'tomkralidis')

assert not is_correct_password(salt, pw_hash, 'Tr0ub4dor&3')

assert not is_correct_password(salt, pw_hash, 'rosebud')
