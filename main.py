import sys
import argparse
from ipUtils import is_valid_ipv4
from ipUtils import secure_encode_decode
from ipUtils import get_local_ip
from types import MappingProxyType
import fullDataClient
import time

STATIC_ADDR = MappingProxyType({
    "IP": "gAAAAABlvXn1cnfI87AdJyJS9Jm2OmVQmuD4w-eIHnz99_IHE4YSVVJd4dgN5jklv7Ao1Z_STnG7apec7xU6Dx134Vu6h8R-Ww==",
    "DH": "gAAAAABlvXnC1tIIltGJI5yos_jO0J76Sqd15m8xA2lNaN6lmAVNfb4_PYqTgviXDkpzhOpkjjdsmaz88w8W26NixDZ3HBA6KQ=="
})

SERVER = "s"
CLIENT = "c"


# usage : main.py s 0.0.0.0
# or
# main.py c DH SeCReT_sEEd#123f
# s = receives the stream
# c = output the stream
def main():
    final_ip = get_local_ip()
    operation_type = SERVER

    # number of args can be 1-4
    if len(sys.argv) == 3:
        # One additional argument provided
        operation_type = sys.argv[1]
        final_ip = sys.argv[2]
        print(f"value received: {final_ip}")
    elif len(sys.argv) == 4:
        # Two additional arguments provided
        operation_type = sys.argv[1]
        name = sys.argv[2]
        seed = sys.argv[3]
        print(f"received name and seed location: {name}, {seed}")
        if name in STATIC_ADDR:
            final_ip = secure_encode_decode(STATIC_ADDR[name], seed, False)
        else:
            print(f"sorry did not find data on name: {name}")
    elif len(sys.argv) > 4:
        usage_msg_and_exit()

    if is_valid_ipv4(final_ip):
        print(f"ip received/configured: {final_ip}")
    else:
        print(f"provided ip is not a valid ip address: {final_ip}")
        usage_msg_and_exit()

    if operation_type == CLIENT:
        print("starting client...")
        fullDataClient.run_full_client(final_ip)
    elif operation_type == SERVER:
        print(f"running the server on the local IP address: {final_ip}...")
        fullDataClient.run_full_server(final_ip)
    else:
        print(f"please provide either s or c for the service specifics")
        usage_msg_and_exit()
    end_msg(True)


def usage_msg_and_exit():
    print(
        "Usage: main.py s/c ${ip address} <-OR-> main.py s/c ${name} ${seed} \n c = client service, s = server "
        "service \n E.G. \n    - main.py s \n    - main.py c 127.0.0.1 \n    - main.py c KEY SuPerSecRet_Seed234kn")
    print(len(sys.argv))
    exit(1)


def end_msg(fast=None):
    if fast:
        print("Operation has come to an end")
    else:
        emulate_typing("operation has cum")
        time.sleep(1)
        emulate_typing("\b\b")
        time.sleep(0.2)
        emulate_typing("ome to an end")
        print('')


def emulate_typing(text, typing_speed=0.2):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(typing_speed)


if __name__ == "__main__":
    main()
