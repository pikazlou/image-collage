import random
import string
import json


def generate_code():
    return ''.join(random.choice(string.ascii_uppercase) for i in range(8))


if __name__ == "__main__":
    codes = [generate_code() for _ in range(126)]
    print(json.dumps(codes))
    grouped = [codes[i:i + 7] for i in range(0, len(codes), 7)]
    for group in grouped:
        print(','.join(group))
