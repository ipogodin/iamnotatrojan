import base64
import socket
import random
import time
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
from hashlib import sha256
from enum import Enum


def simple_encode_decode(value, seed, encode=True):
    try:
        # Generate a key from the seed
        key = sha256(seed.encode()).digest()

        # Prepare the text for XOR operation
        if encode:
            byte_text = value.encode()  # Convert original string to bytes for encoding
        else:
            byte_text = base64.urlsafe_b64decode(value)  # Decode base64 to bytes for decoding

        # XOR the bytes of the text with the bytes of the key
        xor_bytes = bytearray(
            a ^ b for a, b in zip(byte_text, key * (len(byte_text) // len(key)) + key[:len(byte_text) % len(key)]))

        # Return the result
        if encode:
            # If encoding, convert XOR bytes to base64 for readability
            return base64.urlsafe_b64encode(xor_bytes).decode('utf-8')
        else:
            # If decoding, convert XOR bytes directly back to string
            return xor_bytes.decode('utf-8')
    except Exception as e:
        # Log the error message or handle it as needed
        print(f"An error occurred: {e}")
        return ""


def generate_fernet_key(seed):
    """Generate a Fernet key based on a seed."""
    # Use SHA256 to generate a hash from the seed, then use the hash to create a Fernet key
    the_hash = sha256(seed.encode()).digest()
    # Fernet keys must be 32 url-safe base64-encoded bytes
    return urlsafe_b64encode(the_hash)


def secure_encode_decode(value, seed, is_encode=True):
    """Encrypt or decrypt a string using a seed with Fernet symmetric encryption."""
    key = generate_fernet_key(seed)
    fernet = Fernet(key)

    if is_encode:
        # Encrypt the value
        return fernet.encrypt(value.encode()).decode('utf-8')
    else:
        # Decrypt the value
        try:
            return fernet.decrypt(value.encode()).decode('utf-8')
        except Exception as e:
            print(f"Decryption failed: {e}")
            return ""


def is_valid_ipv4(ip):
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    for item in parts:
        if not item.isdigit() or not 0 <= int(item) <= 255:
            return False
    return True


def get_local_ip():
    try:
        # This creates a socket and connects to a public DNS server, then retrieves the socket's own IP.
        # It doesn't actually establish a connection or send data.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error obtaining local IP address: {e}")
        return None


# exponential backoff
def retry_operation(operation_func, max_attempts=5, *args, **kwargs):
    attempt = 1
    operation_result = None
    while attempt <= max_attempts:
        try:
            operation_result = operation_func(*args, **kwargs)
            break
        except Exception as e:
            print(f"Operation failed with error: {e}. Retrying...")
            wait_time = (2 ** (attempt - 1)) + random.random()
            print(f"Waiting {wait_time:.2f} seconds before retrying...")
            time.sleep(wait_time)
            attempt += 1
    else:
        print("All attempts failed.")
    return operation_result


class OperationOutcome(Enum):
    STANDBY = 1
    FAILURE = 2
    RETRY = 3
    EXIT = 4
