import random

def generate_otp():
    id = random.randint(1000, 9999)
    return str(id)
