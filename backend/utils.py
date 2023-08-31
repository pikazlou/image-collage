import random
import string
import json


def generate_code():
    return ''.join(random.choice(string.ascii_uppercase) for i in range(8))


if __name__ == "__main__":
    codes = [generate_code() for _ in range(100)]
    print(json.dumps(codes))
