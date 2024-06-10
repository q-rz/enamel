import random
import string

def rand_parens(size: int, valid: bool = True, par: str = '()', sep = ''): # sep can be None
    if valid:
        size += size % 2
        seq = []
        cnt = 0
        for i in range(size):
            if cnt == 0 or (cnt < size - i and random.randint(0, 1)):
                if cnt == 0:
                    seq.append([])
                seq[-1].append(par[0])
                cnt += 1
            else:
                seq[-1].append(par[1])
                cnt -= 1
        seq = [''.join(subseq) for subseq in seq]
        if sep is not None:
            seq = sep.join(seq)
    else:
        assert sep == ''
        seq = rand_parens(size = (size + 1) // 2 - 1, valid = True, par = par) + par[1] + par[0] + rand_parens(size = (size + 1) // 2 - 1, valid = True, par = par)
    return seq

def miller_rabin(n, k = 5): # Miller--Rabin primality test
    if n == 2 or n == 3:
        return True
    if n == 1 or n % 2 == 0:
        return False
    # Write n as 2^r * d + 1
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    # Witness loop
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False  # n is composite
    return True  # n is probably prime

def rand_probably_prime(lb, ub = None): # [lb, ub]
    if ub is None:
        lb = max(lb, 3)
        lb, ub = lb // 2, lb # Bertrand's postulate
    else:
        lb = max(lb, 0)
        ub = max(lb * 2, ub, 3)
    p = random.randint(lb, ub)
    while not miller_rabin(p):
        p = random.randint(lb, ub)
    return p

def rand_primality(size: int, lid: int, cid: int):
    import random
    size = max(size, 4)
    if lid == 0 and cid == 0:
        n = 2 * 3 * 5 * 7 * 11 * 13 + 1 # == 59 * 509, a composite number
    elif lid == 0 and cid == 1:
        n = 561 # Carmichael's number, a counterexample to the converse of Fermat's little theorem
    elif lid == 0 and cid == 2:
        n = 2
    elif lid == 0 and cid == 3:
        n = 125
    elif cid % 3 == 0:
        n = rand_probably_prime(size)
    elif cid % 3 == 1:
        n = rand_probably_prime(int(size ** 0.5 + 1)) ** 2
    else:
        m = int(size ** 0.5 + 1)
        n = rand_probably_prime(m) * rand_probably_prime(m)
    return n
