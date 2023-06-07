from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def aes_decrypt(iv, salt, password, payload):
    """ Decrypt AndSafe payload

    Keyword arguments:
    :param iv: IV for AES in CBC mode. In hexdecimal string format
    :param salt: salt for scrypt key derivation. In hexdecimal string format
    :param password: password for decryption. In string format
    :param payload: payload to decrypt. In hexdecimal string format
    :return: bytes of decrypted content
    """

    unpadder = padding.PKCS7(128).unpadder()
    backend = default_backend()
    kdf = Scrypt(
        salt=bytes.fromhex(salt),
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=backend)

    key = kdf.derive(password.encode())
    cipher = Cipher(algorithms.AES(key), modes.CBC(bytes.fromhex(iv)), backend=backend)
    decryptor = cipher.decryptor()
    return unpadder.update(decryptor.update(bytes.fromhex(payload)) + decryptor.finalize()) + unpadder.finalize()

def aes_encrypt(iv, salt, password, plain):
    """ Encrypt AndSafe plaintext

    Keyword arguments:
    :param iv: IV for AES in CBC mode. In hexdecimal string format
    :param salt: salt for scrypt key derivation. In hexdecimal string format
    :param password: password for encryption. In string format
    :param plain: plaintext to encrypt
    :return: bytes of encrypted content
    """

    padder = padding.PKCS7(128).padder()
    backend = default_backend()
    kdf = Scrypt(
        salt=bytes.fromhex(salt),
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=backend)

    key = kdf.derive(password.encode())
    cipher = Cipher(algorithms.AES(key), modes.CBC(bytes.fromhex(iv)), backend=backend)
    encryptor = cipher.encryptor()
    return encryptor.update(padder.update(str.encode(plain))+ padder.finalize()) + encryptor.finalize()
