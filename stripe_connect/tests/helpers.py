import string
import random

def random_string(num_chars):
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(num_chars)])
