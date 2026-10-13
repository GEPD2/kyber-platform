"""
ML-KEM (FIPS 203) in pure Python, for the Lab level.

A line-by-line port of the platform's C reference
(tests/data/kyber_fips203_update.c) using hashlib for SHA-3/SHAKE.
tests/test_mlkem.py checks it byte for byte against that C file for
ML-KEM-512/768/1024.

Educational: plain % q arithmetic, data-dependent branches, no zeroisation.
It is not constant-time and must not protect real secrets.
"""
import hashlib

N, Q = 256, 3329
N_INV = 3303  # 128^-1 mod q: the NTT has 7 layers (128 pairs)

PARAMS = {  # k: (eta1, eta2, du, dv)
    2: (3, 2, 10, 4),
    3: (2, 2, 10, 4),
    4: (2, 2, 11, 5),
}
NAMES = {2: 512, 3: 768, 4: 1024}

ZETAS = [
    1, 1729, 2580, 3289, 2642, 630, 1897, 848, 1062, 1919, 193, 797, 2786, 3260, 569, 1746,
    296, 2447, 1339, 1476, 3046, 56, 2240, 1333, 1426, 2094, 535, 2882, 2393, 2879, 1974, 821,
    289, 331, 3253, 1756, 1197, 2304, 2277, 2055, 650, 1977, 2513, 632, 2865, 33, 1320, 1915,
    2319, 1435, 807, 452, 1438, 2868, 1534, 2402, 2647, 2617, 1481, 648, 2474, 3110, 1227, 910,
    17, 2761, 583, 2649, 1637, 723, 2288, 1100, 1409, 2662, 3281, 233, 756, 2156, 3015, 3050,
    1703, 1651, 2789, 1789, 1847, 952, 1461, 2687, 939, 2308, 2437, 2388, 733, 2337, 268, 641,
    1584, 2298, 2037, 3220, 375, 2549, 2090, 1645, 1063, 319, 2773, 757, 2099, 561, 2466, 2594,
    2804, 1092, 403, 1026, 1143, 2150, 2775, 886, 1722, 1212, 1874, 1029, 2110, 2935, 885, 2154,
]


def sizes(k: int) -> dict:
    _, _, du, dv = PARAMS[k]
    return {"ek": 384 * k + 32, "dk": 768 * k + 96, "ct": 32 * (k * du + dv), "ss": 32}


def G(x: bytes) -> tuple[bytes, bytes]:
    h = hashlib.sha3_512(x).digest()
    return h[:32], h[32:]


def H(x: bytes) -> bytes:
    return hashlib.sha3_256(x).digest()


def J(x: bytes) -> bytes:
    return hashlib.shake_256(x).digest(32)


def ntt(f: list[int]) -> list[int]:
    f = list(f)
    k, length = 1, 128
    while length >= 2:
        for start in range(0, N, 2 * length):
            z = ZETAS[k]
            k += 1
            for j in range(start, start + length):
                t = z * f[j + length] % Q
                f[j + length] = (f[j] - t) % Q
                f[j] = (f[j] + t) % Q
        length >>= 1
    return f


def intt(f: list[int]) -> list[int]:
    f = list(f)
    k, length = 127, 2
    while length <= 128:
        for start in range(0, N, 2 * length):
            z = ZETAS[k]
            k -= 1
            for j in range(start, start + length):
                t = f[j]
                f[j] = (t + f[j + length]) % Q
                f[j + length] = z * ((f[j + length] - t) % Q) % Q
        length <<= 1
    return [x * N_INV % Q for x in f]


def basemul(a: list[int], b: list[int]) -> list[int]:
    r = [0] * N
    for g in range(64):
        gp = ZETAS[64 + g]
        for i, gamma in ((4 * g, gp), (4 * g + 2, Q - gp)):
            r[i] = (a[i] * b[i] + gamma * a[i + 1] % Q * b[i + 1]) % Q
            r[i + 1] = (a[i] * b[i + 1] + a[i + 1] * b[i]) % Q
    return r


def add(a: list[int], b: list[int]) -> list[int]:
    return [(x + y) % Q for x, y in zip(a, b)]


def sub(a: list[int], b: list[int]) -> list[int]:
    return [(x - y) % Q for x, y in zip(a, b)]


def sample_ntt(rho: bytes, row: int, col: int) -> list[int]:
    """A[row][col] = SampleNTT(SHAKE128(rho || col || row)), rejection sampling below q."""
    xof = hashlib.shake_128(rho + bytes([col, row]))
    out: list[int] = []
    size = 168 * 4
    stream, pos = xof.digest(size), 0
    while len(out) < N:
        if pos + 3 > len(stream):
            size *= 2
            stream = xof.digest(size)
        b0, b1, b2 = stream[pos], stream[pos + 1], stream[pos + 2]
        pos += 3
        for d in (b0 | ((b1 & 0x0F) << 8), (b1 >> 4) | (b2 << 4)):
            if d < Q and len(out) < N:
                out.append(d)
    return out


def _bit(buf: bytes, t: int) -> int:
    return (buf[t >> 3] >> (t & 7)) & 1


def cbd(buf: bytes, eta: int) -> list[int]:
    out = []
    for i in range(N):
        base = 2 * eta * i
        a = sum(_bit(buf, base + j) for j in range(eta))
        b = sum(_bit(buf, base + eta + j) for j in range(eta))
        out.append((a - b) % Q)
    return out


def sample_poly(seed: bytes, nonce: int, eta: int) -> list[int]:
    return cbd(hashlib.shake_256(seed + bytes([nonce])).digest(64 * eta), eta)


def compress(x: int, d: int) -> int:
    return (((x << d) + Q // 2) // Q) & ((1 << d) - 1)


def decompress(y: int, d: int) -> int:
    return (Q * y + (1 << (d - 1))) >> d


def byte_encode(f: list[int], d: int) -> bytes:
    out = bytearray(32 * d)
    for i, c in enumerate(f):
        v = c & ((1 << d) - 1)
        for b in range(d):
            if (v >> b) & 1:
                out[(i * d + b) >> 3] |= 1 << ((i * d + b) & 7)
    return bytes(out)


def byte_decode(buf: bytes, d: int) -> list[int]:
    out = []
    for i in range(N):
        v = 0
        for b in range(d):
            v |= _bit(buf, i * d + b) << b
        out.append(v % Q if d == 12 else v)
    return out


def poly_compress(f: list[int], d: int) -> bytes:
    return byte_encode([compress(c, d) for c in f], d)


def poly_decompress(buf: bytes, d: int) -> list[int]:
    return [decompress(c, d) for c in byte_decode(buf, d)]


def kpke_keygen(k: int, d: bytes) -> tuple[bytes, bytes]:
    eta1 = PARAMS[k][0]
    rho, sigma = G(d + bytes([k]))
    s = [ntt(sample_poly(sigma, i, eta1)) for i in range(k)]
    e = [ntt(sample_poly(sigma, k + i, eta1)) for i in range(k)]
    t = []
    for i in range(k):
        acc = [0] * N
        for j in range(k):
            acc = add(acc, basemul(sample_ntt(rho, i, j), s[j]))
        t.append(add(acc, e[i]))
    ek = b"".join(byte_encode(p, 12) for p in t) + rho
    dk = b"".join(byte_encode(p, 12) for p in s)
    return ek, dk


def kpke_encrypt(k: int, ek: bytes, m: bytes, coins: bytes) -> bytes:
    eta1, eta2, du, dv = PARAMS[k]
    t = [byte_decode(ek[384 * i:384 * (i + 1)], 12) for i in range(k)]
    rho = ek[384 * k:]
    nonce = 0
    r = []
    for _ in range(k):
        r.append(sample_poly(coins, nonce, eta1))
        nonce += 1
    e1 = []
    for _ in range(k):
        e1.append(sample_poly(coins, nonce, eta2))
        nonce += 1
    e2 = sample_poly(coins, nonce, eta2)
    rhat = [ntt(p) for p in r]
    u = []
    for i in range(k):
        acc = [0] * N
        for j in range(k):
            acc = add(acc, basemul(sample_ntt(rho, j, i), rhat[j]))
        u.append(add(intt(acc), e1[i]))
    acc = [0] * N
    for j in range(k):
        acc = add(acc, basemul(t[j], rhat[j]))
    v = add(add(intt(acc), e2), poly_decompress(m, 1))
    return b"".join(poly_compress(p, du) for p in u) + poly_compress(v, dv)


def kpke_decrypt(k: int, dk: bytes, c: bytes) -> bytes:
    _, _, du, dv = PARAMS[k]
    u = [poly_decompress(c[32 * du * i:32 * du * (i + 1)], du) for i in range(k)]
    v = poly_decompress(c[32 * du * k:], dv)
    s = [byte_decode(dk[384 * i:384 * (i + 1)], 12) for i in range(k)]
    acc = [0] * N
    for j in range(k):
        acc = add(acc, basemul(s[j], ntt(u[j])))
    return poly_compress(sub(v, intt(acc)), 1)


def keygen(k: int, d: bytes, z: bytes) -> tuple[bytes, bytes]:
    """Returns (ek, dk) with dk = dk_PKE || ek || H(ek) || z."""
    ek, dk_pke = kpke_keygen(k, d)
    return ek, dk_pke + ek + H(ek) + z


def encaps(k: int, ek: bytes, m: bytes) -> tuple[bytes, bytes]:
    """Returns (K, c): (K, r) = G(m || H(ek)), c = Encrypt(ek, m; r)."""
    K, r = G(m + H(ek))
    return K, kpke_encrypt(k, ek, m, r)


def decaps(k: int, dk: bytes, c: bytes) -> bytes:
    """Re-encrypt and compare; on mismatch return J(z || c) (implicit rejection)."""
    n = 384 * k
    dk_pke, ek = dk[:n], dk[n:2 * n + 32]
    h, z = dk[2 * n + 32:2 * n + 64], dk[2 * n + 64:]
    m2 = kpke_decrypt(k, dk_pke, c)
    K2, r2 = G(m2 + h)
    return K2 if kpke_encrypt(k, ek, m2, r2) == c else J(z + c)
