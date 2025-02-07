import random

class SuperSecret:
    def __init__(self, nbits=128, p=None, g=None):
        # Generate a safe prime p and compute q = (p-1)//2
        if p is None or g is None:
            self.p = self.gen_safe_prime(nbits)
            # Choose a generator for the subgroup
            self.g = self.choose_generator(self.p)
        else:
            self.p = p
            self.g = g
        self.secret = None
        self.public_key = None
        self.shared_secret = None

    def generate_private_key(self):
        key_size = 512
        self.secret = random.getrandbits(key_size)
    
    def generate_public_key(self):
        self.public_key = pow(self.g, self.secret, self.p)
    
    def generate_shared_secret(self, other_public_key: int):
        self.shared_secret = pow(int(other_public_key), self.secret, self.p)
    
    def miller_rabin_pass(self, a, s, d, n):
        a_to_power = pow(a, d, n)
        if a_to_power == 1:
            return True
        for i in range(s - 1):
            if a_to_power == n - 1:
                return True
            a_to_power = (a_to_power * a_to_power) % n
        return a_to_power == n - 1

    def miller_rabin(self, n):
        d = n - 1
        s = 0
        while d % 2 == 0:
            d >>= 1
            s += 1
        for repeat in range(20):
            a = 0
            while a == 0:
                a = random.randrange(2, n)
            if not self.miller_rabin_pass(a, s, d, n):
                return False
        return True

    def gen_prime(self, nbits):
        while True:
            p = random.getrandbits(nbits)
            # Force candidate to have nbits bits and be odd
            p |= (1 << (nbits - 1)) | 1
            if self.miller_rabin(p):
                return p

    def gen_safe_prime(self, nbits):
        while True:
            q = self.gen_prime(nbits - 1)
            p = 2 * q + 1
            if self.miller_rabin(p):
                return p

    def choose_generator(self, p):
        while True:
            alpha = random.randrange(2, p - 1)
            g = pow(alpha, 2, p)
            if g != 1 and g != p - 1:
                return g

