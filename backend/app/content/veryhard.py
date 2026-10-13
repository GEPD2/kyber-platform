"""
Level 5: Very Hard. Build a mini ML-KEM in Python with the real FIPS 203
hash functions (n = 8, q = 3329, k = 2). Same structure as the standard:
G/H/J/XOF/PRF, domain separation, nonces, the FO transform and implicit
rejection. Checks compare against app/content/toy.py (REF) and against
published SHA-3 known-answer values.
"""
from app.content import cards as C
from app.content.schema import L, choice, gaps, text

S_HASH = L("Hash functions", "Συναρτήσεις hash")
S_PKE = L("K-PKE", "K-PKE")
S_KEM = L("ML-KEM", "ML-KEM")
S_IMPL = L("Implementation", "Υλοποίηση")

HASH_OPTS = ["sha3_512", "sha3_256", "shake_256", "shake_128"]

QUESTIONS = [
gaps("vh-g-ghj", S_HASH,
     L("Assign the right SHA-3 function to G, H and J.", "Αντιστοίχισε τη σωστή συνάρτηση SHA-3 στα G, H και J."),
     "python", """
import hashlib

def G(x):                      # returns two 32-byte halves
    h = hashlib.[[0]](x).digest()
    return h[:32], h[32:]

def H(x):                      # 32-byte hash of the public key
    return hashlib.[[1]](x).digest()

def J(x):                      # 32-byte rejection key
    return hashlib.[[2]](x).digest(32)
""",
     [choice(HASH_OPTS, 0, "hash_role",
             [L("G needs 64 bytes of fixed-length output.", "Το G χρειάζεται 64 bytes εξόδου σταθερού μήκους."),
              L("Fixed output, 512 bits.", "Σταθερή έξοδος, 512 bits.")]),
      choice(HASH_OPTS, 1, "hash_role",
             [L("H outputs exactly 32 bytes, fixed length.", "Το H βγάζει ακριβώς 32 bytes, σταθερό μήκος."),
              L("Fixed output, 256 bits.", "Σταθερή έξοδος, 256 bits.")]),
      choice(HASH_OPTS, 2, "hash_role",
             [L("J takes a length argument, so it is an XOF.", "Το J παίρνει όρισμα μήκους, άρα είναι XOF."),
              L("The XOF with the higher security level.", "Το XOF με το υψηλότερο επίπεδο ασφάλειας.")])],
     C.HASHES,
     L("G = SHA3-512, H = SHA3-256, J = SHAKE256. The check also compares with the published empty-string test vectors.",
       "G = SHA3-512, H = SHA3-256, J = SHAKE256. Ο έλεγχος συγκρίνει και με τα δημοσιευμένα test vectors κενής εισόδου."),
     check=("assert H(b'').hex() == 'a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a'\n"
            "assert b''.join(G(b'')).hex().startswith('a69f73cca23a9ac5c8b567dc185a756e')\n"
            "assert J(b'').hex() == '46b9dd2b0ba88d13233b3feb743eeb243fcd52ea62b81b82b50c27646ed5762f'\n"
            "for x in (b'abc', bytes(range(40))):\n"
            "    assert G(x) == REF.G(x) and H(x) == REF.H(x) and J(x) == REF.J(x)")),

gaps("vh-g-xof-prf", S_HASH,
     L("Complete the XOF (matrix A) and the PRF (noise).", "Συμπλήρωσε το XOF (πίνακας A) και την PRF (θόρυβος)."),
     "python", """
def XOF(rho, i, j, length):        # for entry A[i][j]
    return hashlib.[[0]](rho + bytes([[[1]]])).digest(length)

def PRF(seed, nonce, length):
    return hashlib.[[2]](seed + bytes([nonce])).digest(length)
""",
     [choice(["shake_128", "shake_256"], 0, "hash_role",
             [L("The public matrix is expanded with the faster XOF.", "Ο δημόσιος πίνακας επεκτείνεται με το γρηγορότερο XOF."),
              L("128-bit security level.", "Επίπεδο ασφάλειας 128 bits.")]),
      choice(["j, i", "i, j"], 0, "matrix",
             [L("FIPS 203 appends the column index first.", "Το FIPS 203 προσθέτει πρώτα τον δείκτη στήλης."),
              L("The input is ρ ‖ j ‖ i.", "Η είσοδος είναι ρ ‖ j ‖ i.")]),
      choice(["shake_128", "shake_256"], 1, "hash_role",
             [L("Secret noise uses the other SHAKE.", "Ο μυστικός θόρυβος χρησιμοποιεί το άλλο SHAKE."),
              L("256-bit security level.", "Επίπεδο ασφάλειας 256 bits.")])],
     C.HASHES,
     L("XOF = SHAKE128(ρ ‖ j ‖ i), PRF = SHAKE256(σ ‖ N). Swapping them, or i and j, gives a different matrix.",
       "XOF = SHAKE128(ρ ‖ j ‖ i), PRF = SHAKE256(σ ‖ N). Αν τα μπερδέψεις, ή τα i και j, προκύπτει άλλος πίνακας."),
     check=("rho = bytes(range(32))\n"
            "assert XOF(rho, 0, 1, 40) == REF.XOF(rho, 0, 1, 40)\n"
            "assert XOF(rho, 1, 0, 40) == REF.XOF(rho, 1, 0, 40)\n"
            "assert PRF(rho, 3, 40) == REF.PRF(rho, 3, 40)")),

gaps("vh-g-sample-ntt", S_PKE,
     L("Complete SampleNTT: rejection-sample 12-bit values below q.", "Συμπλήρωσε το SampleNTT: δειγματοληψία με απόρριψη τιμών 12 bits κάτω από q."),
     "python", """
def sample_ntt(rho, i, j, q=MQ):
    out, stream, pos = [], XOF(rho, i, j, 168), 0
    while len(out) < N:
        b0, b1, b2 = stream[pos:pos + 3]; pos += 3
        d1 = b0 | ((b1 & 0x0F) << 8)
        d2 = [[0]]
        for d in (d1, d2):
            if [[1]] and len(out) < N:
                out.append(d)
    return out
""",
     [choice(["(b1 >> 4) | (b2 << 4)", "(b1 & 0x0F) | (b2 << 4)", "b2 << 8", "(b1 >> 4) | (b2 << 8)"], 0, "sampling",
             [L("3 bytes = 24 bits = two 12-bit numbers; d1 used the low nibble of b1.", "3 bytes = 24 bits = δύο αριθμοί των 12 bits· το d1 πήρε το χαμηλό nibble του b1."),
              L("d2 = high nibble of b1, then all 8 bits of b2 above it.", "d2 = ανώτερο nibble του b1, και από πάνω όλα τα 8 bits του b2.")]),
      choice(["d < q", "d < 4096", "d % q"], 0, "sampling",
             [L("Reducing mod q would make small values more likely.", "Η αναγωγή mod q θα έκανε τις μικρές τιμές πιο πιθανές."),
              L("Throw away anything that is not already in Z_q.", "Πέτα ό,τι δεν είναι ήδη στο Z_q.")])],
     C.HASHES,
     L("Rejecting d ≥ q keeps A exactly uniform; taking d mod q would bias it. The values are used directly as NTT coefficients.",
       "Η απόρριψη των d ≥ q κρατά τον A ακριβώς ομοιόμορφο· το d mod q θα τον στρέβλωνε. Οι τιμές χρησιμοποιούνται απευθείας ως συντελεστές NTT."),
     check=("rho = bytes(range(32))\n"
            "for i, j in [(0, 0), (0, 1), (1, 0), (1, 1)]:\n"
            "    assert sample_ntt(rho, i, j) == REF.sample_ntt(rho, i, j)")),

gaps("vh-g-sample-cbd", S_PKE,
     L("How many PRF bytes does one η = 2 noise polynomial need (n = 8)?", "Πόσα bytes PRF χρειάζεται ένα πολυώνυμο θορύβου η = 2 (n = 8);"),
     "python", """
def sample_cbd(seed, nonce, q=MQ):
    return cbd_eta2(PRF(seed, nonce, [[0]]), q)
""",
     [text(["N // 2", "4", "N >> 1"], "cbd",
           [L("Each coefficient uses 2η = 4 bits.", "Κάθε συντελεστής χρησιμοποιεί 2η = 4 bits."),
            L("n coefficients × 4 bits, divided by 8 bits per byte.", "n συντελεστές × 4 bits, διά 8 bits ανά byte.")], width=7)],
     C.CBD,
     L("4n bits = n/2 bytes. For n = 256 that is 128 = 64·η bytes, exactly what FIPS 203 asks of the PRF.",
       "4n bits = n/2 bytes. Για n = 256 αυτό είναι 128 = 64·η bytes, ακριβώς ό,τι ζητά το FIPS 203 από την PRF."),
     check="assert sample_cbd(bytes(32), 3) == REF.sample_cbd(bytes(32), 3) and len(sample_cbd(bytes(32), 0)) == N"),

gaps("vh-g-keygen", S_PKE,
     L("Complete K-PKE.KeyGen: seeds and noise nonces.", "Συμπλήρωσε το K-PKE.KeyGen: σπόροι και nonces θορύβου."),
     "python", """
def pke_keygen(d, q=MQ):
    rho, sigma = G(d + bytes([[[0]]]))
    A_hat = [[sample_ntt(rho, i, j, q) for j in range(K)] for i in range(K)]
    s = [sample_cbd(sigma, i, q) for i in range(K)]
    e = [sample_cbd(sigma, [[1]], q) for i in range(K)]
    t_hat, s_hat = keygen(A_hat, s, e, q)
    return (t_hat, rho), s_hat
""",
     [text(["K", "2"], "hash_role",
           [L("FIPS 203 binds the parameter set into the seed (domain separation).", "Το FIPS 203 δένει το σύνολο παραμέτρων μέσα στον σπόρο (domain separation)."),
            L("Append the module rank as one byte: G(d ‖ k).", "Πρόσθεσε την τάξη του module ως ένα byte: G(d ‖ k).")], width=4),
      choice(["K + i", "i", "i + 1", "2 * i"], 0, "noise",
             [L("Every noise polynomial needs its own nonce.", "Κάθε πολυώνυμο θορύβου χρειάζεται δικό του nonce."),
              L("s used nonces 0 … k−1; e continues after them.", "Το s πήρε nonces 0 … k−1· το e συνεχίζει μετά.")])],
     C.KEYGEN,
     L("(ρ, σ) = G(d ‖ k); s uses nonces 0…k−1 and e uses k…2k−1. Reusing a nonce would make e equal to s.",
       "(ρ, σ) = G(d ‖ k)· το s χρησιμοποιεί nonces 0…k−1 και το e k…2k−1. Αν ξαναχρησιμοποιηθεί nonce, το e γίνεται ίσο με το s."),
     check="d = bytes(range(32))\nassert pke_keygen(d) == REF.pke_keygen(d)"),

gaps("vh-g-encrypt", S_PKE,
     L("Complete the noise nonces in K-PKE.Encrypt.", "Συμπλήρωσε τα nonces θορύβου στο K-PKE.Encrypt."),
     "python", """
def pke_encrypt(ek, m, coins, q=MQ):
    t_hat, rho = ek
    A_hat = [[sample_ntt(rho, i, j, q) for j in range(K)] for i in range(K)]
    r = [sample_cbd(coins, i, q) for i in range(K)]
    e1 = [sample_cbd(coins, [[0]], q) for i in range(K)]
    e2 = sample_cbd(coins, [[1]], q)
    return encrypt(A_hat, t_hat, r, e1, e2, bytes_to_bits(m), q)
""",
     [choice(["K + i", "i", "2 * K + i"], 0, "noise",
             [L("r took nonces 0 … k−1.", "Το r πήρε nonces 0 … k−1."),
              L("e₁ follows directly after r.", "Το e₁ ακολουθεί αμέσως μετά το r.")]),
      text(["2 * K", "4", "K + K"], "noise",
           [L("One more polynomial after r and e₁.", "Ένα ακόμη πολυώνυμο μετά τα r και e₁."),
            L("r and e₁ used 2k nonces in total.", "Τα r και e₁ χρησιμοποίησαν συνολικά 2k nonces.")], width=6)],
     C.ENCRYPT,
     L("Nonces run 0…k−1 (r), k…2k−1 (e₁), 2k (e₂). Encryption is deterministic given the coins, which the FO transform relies on.",
       "Τα nonces είναι 0…k−1 (r), k…2k−1 (e₁), 2k (e₂). Η κρυπτογράφηση είναι ντετερμινιστική για δεδομένα νομίσματα, και σε αυτό στηρίζεται ο FO."),
     check=("ek, _ = REF.pke_keygen(bytes(32))\n"
            "coins = bytes(range(32))\n"
            "assert pke_encrypt(ek, b'\\x5a', coins) == REF.pke_encrypt(ek, b'\\x5a', coins)")),

gaps("vh-g-bits", S_PKE,
     L("Message bytes to bits, least-significant bit first (FIPS 203 ByteDecode).", "Bytes μηνύματος σε bits, πρώτα το λιγότερο σημαντικό (FIPS 203 ByteDecode)."),
     "python", """
def bytes_to_bits(m):
    return [(m[i // 8] >> ([[0]])) & 1 for i in range(8 * len(m))]
""",
     [text(["i % 8", "i & 7"], "encode",
           [L("Bit i of the message lives in byte i // 8.", "Το bit i του μηνύματος βρίσκεται στο byte i // 8."),
            L("Its position inside that byte is the remainder.", "Η θέση του μέσα σε εκείνο το byte είναι το υπόλοιπο.")], width=6)],
     C.ENCRYPT,
     L("Shift by i mod 8, LSB first. Reading MSB first gives a valid-looking but incompatible encoding.",
       "Ολίσθηση κατά i mod 8, πρώτα το LSB. Αν διαβάσεις πρώτα το MSB βγαίνει κωδικοποίηση που φαίνεται σωστή αλλά δεν είναι συμβατή."),
     check=("assert bytes_to_bits(b'\\x01\\x80') == [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]\n"
            "assert REF.bits_to_bytes(bytes_to_bits(b'\\x5a\\xc3')) == b'\\x5a\\xc3'")),

gaps("vh-g-kem-keygen", S_KEM,
     L("Complete the decapsulation key layout.", "Συμπλήρωσε τη διάταξη του κλειδιού αποσυσκευασίας."),
     "python", """
def kem_keygen(d, z):
    ek, dk_pke = pke_keygen(d)
    return ek, (dk_pke, ek, [[0]], z)
""",
     [choice(["H(ek_bytes(ek))", "G(ek_bytes(ek))", "ek_bytes(ek)", "H(z)"], 0, "fo_transform",
             [L("Decapsulation needs a 32-byte digest of the public key.", "Η αποσυσκευασία χρειάζεται ένα digest 32 bytes του δημόσιου κλειδιού."),
              L("dk = dk_PKE ‖ ek ‖ H(ek) ‖ z.", "dk = dk_PKE ‖ ek ‖ H(ek) ‖ z.")])],
     C.FO,
     L("Storing H(ek) saves rehashing the key on every decapsulation; z is the implicit-rejection secret.",
       "Η αποθήκευση του H(ek) γλιτώνει το ξανά-hash του κλειδιού σε κάθε αποσυσκευασία· το z είναι το μυστικό της implicit rejection."),
     check="d, z = bytes(range(32)), bytes(range(32, 64))\nassert kem_keygen(d, z) == REF.kem_keygen(d, z)"),

gaps("vh-g-encaps", S_KEM,
     L("Complete ML-KEM.Encaps.", "Συμπλήρωσε το ML-KEM.Encaps."),
     "python", """
def kem_encaps(ek, m):
    K_shared, r = G(m + [[0]])
    c = pke_encrypt(ek, m, [[1]])
    return K_shared, c
""",
     [choice(["H(ek_bytes(ek))", "ek_bytes(ek)", "H(m)", "J(ek_bytes(ek))"], 0, "fo_transform",
             [L("Bind the key to this specific public key.", "Δέσε το κλειδί με αυτό το συγκεκριμένο δημόσιο κλειδί."),
              L("(K, r) = G(m ‖ H(ek)).", "(K, r) = G(m ‖ H(ek)).")]),
      choice(["r", "K_shared", "m", "H(m)"], 0, "fo_transform",
             [L("The encryption randomness is derived, not fresh.", "Η τυχαιότητα της κρυπτογράφησης παράγεται, δεν είναι φρέσκια."),
              L("Use the second half of G's output.", "Χρησιμοποίησε το δεύτερο μισό της εξόδου του G.")])],
     C.FO,
     L("The coins r come from m, so the decapsulator can recompute the exact ciphertext. K is never hashed with c in FIPS 203.",
       "Τα νομίσματα r προκύπτουν από το m, ώστε ο αποσυσκευαστής να ξαναϋπολογίσει ακριβώς το ίδιο κρυπτογράφημα. Στο FIPS 203 το K δεν γίνεται ποτέ hash μαζί με το c."),
     check=("ek, _ = REF.kem_keygen(bytes(32), bytes(32))\n"
            "assert kem_encaps(ek, b'\\x37') == REF.kem_encaps(ek, b'\\x37')")),

gaps("vh-g-decaps", S_KEM,
     L("Complete ML-KEM.Decaps: re-encrypt, compare, reject implicitly.", "Συμπλήρωσε το ML-KEM.Decaps: επανακρυπτογράφηση, σύγκριση, implicit rejection."),
     "python", """
def kem_decaps(dk, c):
    dk_pke, ek, h, z = dk
    m2 = pke_decrypt(dk_pke, c)
    K2, r2 = G(m2 + h)
    c2 = [[0]]
    K_bar = J([[1]])
    return K2 if [[2]] else K_bar
""",
     [choice(["pke_encrypt(ek, m2, r2)", "pke_encrypt(ek, m2, K2)", "c"], 0, "fo_transform",
             [L("Repeat exactly what an honest sender would have done.", "Επανάλαβε ακριβώς ό,τι θα έκανε ένας τίμιος αποστολέας."),
              L("Encrypt m′ with the re-derived coins.", "Κρυπτογράφησε το m′ με τα νομίσματα που ξαναπαράχθηκαν.")]),
      choice(["z + ct_bytes(c)", "ct_bytes(c)", "z", "h + ct_bytes(c)"], 0, "implicit_reject",
             [L("The attacker must not be able to compute the rejection key.", "Ο επιτιθέμενος δεν πρέπει να μπορεί να υπολογίσει το κλειδί απόρριψης."),
              L("Mix a secret with the ciphertext: J(z ‖ c).", "Ανάμειξε ένα μυστικό με το κρυπτογράφημα: J(z ‖ c).")]),
      choice(["c2 == c", "m2 == m", "K2 == K_bar", "True"], 0, "implicit_reject",
             [L("Accept only if the ciphertext is exactly what m′ would produce.", "Δέξου μόνο αν το κρυπτογράφημα είναι ακριβώς αυτό που θα έβγαζε το m′."),
              L("Compare the re-encryption with what was received.", "Σύγκρινε την επανακρυπτογράφηση με αυτό που έφτασε.")])],
     C.FO,
     L("A tampered ciphertext yields J(z ‖ c): a stable key that looks random and reveals nothing. In C this comparison must be constant-time.",
       "Ένα αλλοιωμένο κρυπτογράφημα δίνει J(z ‖ c): ένα σταθερό κλειδί που μοιάζει τυχαίο και δεν αποκαλύπτει τίποτα. Στη C η σύγκριση πρέπει να είναι σταθερού χρόνου."),
     check=("d, z = bytes(range(32)), bytes(range(32, 64))\n"
            "ek, dk = REF.kem_keygen(d, z)\n"
            "Ks, c = REF.kem_encaps(ek, b'\\x37')\n"
            "assert kem_decaps(dk, c) == Ks\n"
            "u, v = c\n"
            "bad = (u, [(v[0] + 1000) % MQ] + v[1:])\n"
            "assert kem_decaps(dk, bad) == REF.J(z + REF.ct_bytes(bad)) != Ks")),

gaps("vh-g-sizes", S_KEM,
     L("Byte sizes of the real parameter sets.", "Μεγέθη σε bytes των πραγματικών συνόλων παραμέτρων."),
     "python", """
def ek_len(k):
    return 384 * k + 32                 # t (12 bits x 256) and rho

def ct_len(k, du, dv):
    return 32 * ([[0]])

def dk_len(k):
    return 384 * k + [[1]] + 32 + 32    # dk_pke, ek, H(ek), z
""",
     [text(["k * du + dv", "du * k + dv", "dv + k * du", "dv + du * k"], "sizes",
           [L("u has k polynomials compressed to dᵤ bits, v one polynomial to dᵥ bits.", "Το u έχει k πολυώνυμα συμπιεσμένα σε dᵤ bits, το v ένα πολυώνυμο σε dᵥ bits."),
            L("256 coefficients × d bits = 32·d bytes per polynomial.", "256 συντελεστές × d bits = 32·d bytes ανά πολυώνυμο.")], width=10),
      choice(["ek_len(k)", "384 * k", "32"], 0, "sizes",
             [L("The decapsulation key carries a full copy of the public key.", "Το κλειδί αποσυσκευασίας περιέχει πλήρες αντίγραφο του δημόσιου κλειδιού."),
              L("dk = dk_PKE ‖ ek ‖ H(ek) ‖ z.", "dk = dk_PKE ‖ ek ‖ H(ek) ‖ z.")])],
     C.SIZES,
     L("ct = 32(k·dᵤ + dᵥ); dk = 384k + ek + 64. These give 768/1088/1568 and 1632/2400/3168 bytes.",
       "ct = 32(k·dᵤ + dᵥ)· dk = 384k + ek + 64. Αυτά δίνουν 768/1088/1568 και 1632/2400/3168 bytes."),
     check=("assert [ct_len(2, 10, 4), ct_len(3, 10, 4), ct_len(4, 11, 5)] == [768, 1088, 1568]\n"
            "assert [dk_len(k) for k in (2, 3, 4)] == [1632, 2400, 3168]")),

gaps("vh-g-ct-equal", S_IMPL,
     L("Compare two ciphertexts without an early exit.", "Σύγκρινε δύο κρυπτογραφήματα χωρίς πρόωρη έξοδο."),
     "python", """
def ct_equal(a, b):
    if len(a) != len(b):
        return False
    diff = 0
    for x, y in zip(a, b):
        diff [[0]] x ^ y
    return diff == 0
""",
     [choice(["|=", "=", "&="], 0, "constant_time",
             [L("Every byte must be looked at, and any difference must stick.", "Κάθε byte πρέπει να ελεγχθεί, και κάθε διαφορά πρέπει να «μείνει»."),
              L("Accumulate the XORs with a bitwise OR.", "Συσσώρευσε τα XOR με bitwise OR.")])],
     C.FO,
     L("OR-accumulating XORs touches every byte and leaks no position. Python itself is not constant-time; use hmac.compare_digest in real code.",
       "Η συσσώρευση XOR με OR αγγίζει κάθε byte και δεν διαρρέει θέση. Η ίδια η Python δεν είναι σταθερού χρόνου· σε πραγματικό κώδικα χρησιμοποίησε hmac.compare_digest."),
     check=("assert ct_equal(b'abc', b'abc')\n"
            "assert not ct_equal(b'abc', b'abd') and not ct_equal(b'xbc', b'abc')")),
]
