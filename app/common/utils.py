from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


def load_private_key(private_key_bytes, private_key_passphrase):
    p_key = serialization.load_pem_private_key(
        private_key_bytes,
        password=private_key_passphrase.encode("utf-8"),
        backend=default_backend(),
    )
    pkb = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return pkb
