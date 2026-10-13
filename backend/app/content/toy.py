"""
Toy Kyber used by every Python question: q=17, n=8, k=2.

The ring is Z_17[X]/(X^8+1) (negacyclic, like real Kyber). 17 has a primitive
16th root psi=3, so the toy NTT is a FULL negacyclic NTT: twist by psi^i, run a
cyclic NTT with omega=psi^2=9, multiply pointwise. Real Kyber (q=3329, n=256)
has no primitive 512th root, so its NTT stops after 7 layers at 128 pairs and
multiplies with basemul instead. The questions point this difference out.

Encodings follow the teaching reference: bit 1 -> floor(q/2) = 8.
This module is the executable ground truth for the content self-check.
"""

Q, N, K = 17, 8, 2
PSI, PSI_INV = 3, 6
OMEGA, OMEGA_INV = 9, 2
N_INV = 15
HALF_Q = Q // 2


def modpow(base, exp, mod):
    result, b = 1, base % mod
    while exp > 0:
        if exp & 1:
            result = result * b % mod
        b = b * b % mod
        exp >>= 1
    return result


ROOTS = [modpow(OMEGA, i, Q) for i in range(N)]
INV_ROOTS = [modpow(OMEGA_INV, i, Q) for i in range(N)]


def cbd_eta2(byte_list, q=Q):
    out = []
    for byte_val in byte_list:
        bits = [(byte_val >> i) & 1 for i in range(8)]
        for pair in range(2):
            b0, b1, b2, b3 = bits[pair * 4:pair * 4 + 4]
            out.append(((b0 + b1) - (b2 + b3)) % q)
    return out


def bit_reverse(i, bits):
    return int(format(i, f"0{bits}b")[::-1], 2)


def bit_reverse_permute(a):
    n = len(a)
    bits = n.bit_length() - 1
    r = list(a)
    for i in range(n):
        j = bit_reverse(i, bits)
        if j > i:
            r[i], r[j] = r[j], r[i]
    return r


def butterfly(u, v, w, q=Q):
    t = v * w % q
    return (u + t) % q, (u - t) % q


def ntt_cyclic(poly, roots, q=Q):
    n = len(poly)
    a = bit_reverse_permute(poly)
    length = 2
    while length <= n:
        step = n // length
        for start in range(0, n, length):
            for j in range(length // 2):
                f, s = start + j, start + j + length // 2
                a[f], a[s] = butterfly(a[f], a[s], roots[j * step], q)
        length <<= 1
    return a


_TABLES = {}


def primitive_root(q):
    factors = {f for f in range(2, q) if (q - 1) % f == 0 and all(f % d for d in range(2, f))}
    return next(g for g in range(2, q) if all(modpow(g, (q - 1) // f, q) != 1 for f in factors))


def tables(q, n=N):
    """psi, psi^-1, omega roots, inverse roots, n^-1 for Z_q[X]/(X^n+1)."""
    if (q, n) not in _TABLES:
        psi = modpow(primitive_root(q), (q - 1) // (2 * n), q)
        psi_inv = modpow(psi, q - 2, q)
        omega, omega_inv = psi * psi % q, psi_inv * psi_inv % q
        _TABLES[(q, n)] = {
            "psi": psi, "psi_inv": psi_inv,
            "roots": [modpow(omega, i, q) for i in range(n)],
            "inv_roots": [modpow(omega_inv, i, q) for i in range(n)],
            "n_inv": modpow(n, q - 2, q),
        }
    return _TABLES[(q, n)]


def twist(poly, q=Q):
    psi = tables(q, len(poly))["psi"]
    return [c * modpow(psi, i, q) % q for i, c in enumerate(poly)]


def untwist(poly, q=Q):
    psi_inv = tables(q, len(poly))["psi_inv"]
    return [c * modpow(psi_inv, i, q) % q for i, c in enumerate(poly)]


def ntt(poly, q=Q):
    return ntt_cyclic(twist(poly, q), tables(q, len(poly))["roots"], q)


def intt(poly_hat, q=Q):
    t = tables(q, len(poly_hat))
    a = ntt_cyclic(poly_hat, t["inv_roots"], q)
    return untwist([c * t["n_inv"] % q for c in a], q)


def schoolbook_mul(a, b, q=Q):
    n = len(a)
    r = [0] * n
    for i in range(n):
        for j in range(n):
            k = i + j
            if k < n:
                r[k] = (r[k] + a[i] * b[j]) % q
            else:
                r[k - n] = (r[k - n] - a[i] * b[j]) % q
    return r


def pointwise_mul(a, b, q=Q):
    return [x * y % q for x, y in zip(a, b)]


def poly_add(a, b, q=Q):
    return [(x + y) % q for x, y in zip(a, b)]


def poly_sub(a, b, q=Q):
    return [(x - y) % q for x, y in zip(a, b)]


def transpose(M):
    k = len(M)
    return [[M[j][i] for j in range(k)] for i in range(k)]


def matvec_ntt(M, v_hat, q=Q):
    out = []
    for row in range(len(M)):
        acc = [0] * len(v_hat[0])
        for col in range(len(M)):
            acc = poly_add(acc, pointwise_mul(M[row][col], v_hat[col], q), q)
        out.append(acc)
    return out


def inner_ntt(a_hat, b_hat, q=Q):
    acc = [0] * len(a_hat[0])
    for x, y in zip(a_hat, b_hat):
        acc = poly_add(acc, pointwise_mul(x, y, q), q)
    return acc


def encode_message(bits, q=Q):
    return [b * (q // 2) for b in bits]


def decode_bit(c, q=Q):
    d0 = min(c, q - c)
    dq2 = min(abs(c - q // 2), q - abs(c - q // 2))
    return 1 if dq2 < d0 else 0


def keygen(A_hat, s, e, q=Q):
    s_hat = [ntt(p, q) for p in s]
    e_hat = [ntt(p, q) for p in e]
    t_hat = [poly_add(row, eh, q) for row, eh in zip(matvec_ntt(A_hat, s_hat, q), e_hat)]
    return t_hat, s_hat


def encrypt(A_hat, t_hat, r, e1, e2, msg, q=Q):
    r_hat = [ntt(p, q) for p in r]
    u = [poly_add(intt(x, q), y, q) for x, y in zip(matvec_ntt(transpose(A_hat), r_hat, q), e1)]
    v = poly_add(poly_add(intt(inner_ntt(t_hat, r_hat, q), q), e2, q), encode_message(msg, q), q)
    return u, v


def decrypt(s_hat, u, v, q=Q):
    u_hat = [ntt(p, q) for p in u]
    w = poly_sub(v, intt(inner_ntt(s_hat, u_hat, q), q), q)
    return [decode_bit(c, q) for c in w], w


def centered(c, q=Q):
    return c - q if c > q // 2 else c


# Mini ML-KEM for the Very Hard level: the FIPS 203 structure (G, H, J, XOF,
# PRF, the FO transform, implicit rejection) with the real SHA-3 / SHAKE
# functions, but n = 8 so everything fits on screen. q = 3329 keeps the
# decryption noise far below q/4 with random CBD noise; with q = 17 it would
# fail often. No compression here; the C level covers it.
import hashlib

MQ = 3329


def G(x):
    h = hashlib.sha3_512(x).digest()
    return h[:32], h[32:]


def H(x):
    return hashlib.sha3_256(x).digest()


def J(x):
    return hashlib.shake_256(x).digest(32)


def XOF(rho, i, j, length):
    return hashlib.shake_128(rho + bytes([j, i])).digest(length)


def PRF(seed, nonce, length):
    return hashlib.shake_256(seed + bytes([nonce])).digest(length)


def sample_ntt(rho, i, j, q=MQ):
    out, stream, pos = [], XOF(rho, i, j, 168), 0
    while len(out) < N:
        b0, b1, b2 = stream[pos:pos + 3]
        pos += 3
        d1 = b0 | ((b1 & 0x0F) << 8)
        d2 = (b1 >> 4) | (b2 << 4)
        for d in (d1, d2):
            if d < q and len(out) < N:
                out.append(d)
    return out


def sample_cbd(seed, nonce, q=MQ):
    return cbd_eta2(PRF(seed, nonce, N // 2), q)


def poly_bytes(polys):
    return b"".join(c.to_bytes(2, "little") for p in polys for c in p)


def ek_bytes(ek):
    t_hat, rho = ek
    return poly_bytes(t_hat) + rho


def ct_bytes(c):
    u, v = c
    return poly_bytes(u + [v])


def bytes_to_bits(m):
    return [(m[i // 8] >> (i % 8)) & 1 for i in range(8 * len(m))]


def bits_to_bytes(bits):
    return bytes(sum(bits[8 * i + j] << j for j in range(8)) for i in range(len(bits) // 8))


def pke_keygen(d, q=MQ):
    rho, sigma = G(d + bytes([K]))
    A_hat = [[sample_ntt(rho, i, j, q) for j in range(K)] for i in range(K)]
    s = [sample_cbd(sigma, i, q) for i in range(K)]
    e = [sample_cbd(sigma, K + i, q) for i in range(K)]
    t_hat, s_hat = keygen(A_hat, s, e, q)
    return (t_hat, rho), s_hat


def pke_encrypt(ek, m, coins, q=MQ):
    t_hat, rho = ek
    A_hat = [[sample_ntt(rho, i, j, q) for j in range(K)] for i in range(K)]
    r = [sample_cbd(coins, i, q) for i in range(K)]
    e1 = [sample_cbd(coins, K + i, q) for i in range(K)]
    e2 = sample_cbd(coins, 2 * K, q)
    return encrypt(A_hat, t_hat, r, e1, e2, bytes_to_bits(m), q)


def pke_decrypt(s_hat, c, q=MQ):
    u, v = c
    bits, _ = decrypt(s_hat, u, v, q)
    return bits_to_bytes(bits)


def kem_keygen(d, z):
    ek, dk_pke = pke_keygen(d)
    return ek, (dk_pke, ek, H(ek_bytes(ek)), z)


def kem_encaps(ek, m):
    K_shared, r = G(m + H(ek_bytes(ek)))
    return K_shared, pke_encrypt(ek, m, r)


def kem_decaps(dk, c):
    dk_pke, ek, h, z = dk
    m2 = pke_decrypt(dk_pke, c)
    K2, r2 = G(m2 + h)
    c2 = pke_encrypt(ek, m2, r2)
    K_bar = J(z + ct_bytes(c))
    return K2 if c2 == c else K_bar


# The fixed worked instance used across levels. Noise kept sparse so the
# total decryption noise stays below q/4 = 4.25 on every coefficient.
A_HAT = [
    [[2, 11, 5, 0, 7, 3, 14, 9], [6, 6, 1, 12, 4, 16, 8, 2]],
    [[13, 1, 9, 4, 10, 2, 5, 15], [3, 7, 0, 8, 11, 6, 1, 4]],
]
S = [[1, 0, 16, 1, 0, 0, 0, 1], [0, 1, 0, 0, 16, 0, 1, 0]]
E = [[1, 0, 0, 16, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 16]]
R = [[1, 0, 0, 0, 0, 16, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0]]
E1 = [[0, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 16, 0, 0]]
E2 = [0, 0, 0, 1, 0, 0, 0, 0]
MSG = [1, 0, 1, 1, 0, 0, 1, 0]
