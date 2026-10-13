"""
Level 4: Hard. FIPS 203 facts, then code that builds the toy NTT and the
CPA encryption. Mostly multiple choice; the few typed gaps are numbers or
formulas with every accepted form listed.
"""
from app.content import cards as C
from app.content.schema import L, btns, choice, gaps, text

S_SEC = L("Security", "Ασφάλεια")
S_FIPS = L("FIPS 203", "FIPS 203")
S_NTT = L("NTT", "NTT")
S_ENC = L("Encryption", "Κρυπτογράφηση")

QUESTIONS = [
btns("ha-mlwe", S_SEC,
     L("The MLWE assumption says that (A, A·s + e) is…", "Η υπόθεση MLWE λέει ότι το (A, A·s + e) είναι…"),
     [L("easy to invert with Gaussian elimination", "εύκολο να αντιστραφεί με απαλοιφή Gauss"),
      L("hard to tell apart from (A, uniform random)", "δύσκολο να ξεχωρίσει από το (A, ομοιόμορφα τυχαίο)"),
      L("secure only against classical computers", "ασφαλές μόνο απέναντι σε κλασικούς υπολογιστές"),
      L("a periodic function of s", "περιοδική συνάρτηση του s")], 1, C.KEYGEN,
     [L("It is a statement about what an attacker cannot distinguish.", "Είναι δήλωση για το τι δεν μπορεί να ξεχωρίσει ένας επιτιθέμενος."),
      L("Compare against truly random vectors.", "Σύγκρινε με πραγματικά τυχαία διανύσματα.")],
     L("Decision-MLWE: the public key looks random. Without e, Gaussian elimination would recover s.",
       "Decision-MLWE: το δημόσιο κλειδί μοιάζει τυχαίο. Χωρίς το e, η απαλοιφή Gauss θα ανακτούσε το s.")),

btns("ha-order", S_NTT,
     L("To prove g has order 16 mod 17 it is enough to check…", "Για να αποδείξεις ότι το g έχει τάξη 16 mod 17 αρκεί να ελέγξεις…"),
     ["g¹⁶ ≡ 1", "g⁸ ≢ 1", "g² ≢ 1", L("g is odd", "το g είναι περιττό")], 1, C.ROOTS,
     [L("The order must divide 16 = 2⁴.", "Η τάξη πρέπει να διαιρεί το 16 = 2⁴."),
      L("Every proper divisor of 16 divides 8.", "Κάθε γνήσιος διαιρέτης του 16 διαιρεί το 8.")],
     L("If g⁸ ≢ 1, the order is not 1, 2, 4 or 8, so it is 16. g¹⁶ ≡ 1 holds for every g (Fermat).",
       "Αν g⁸ ≢ 1, η τάξη δεν είναι 1, 2, 4 ή 8, άρα είναι 16. Το g¹⁶ ≡ 1 ισχύει για κάθε g (Fermat).")),

btns("ha-g", S_FIPS,
     L("In FIPS 203, G is…", "Στο FIPS 203, το G είναι…"),
     ["SHAKE128", "SHA3-256", "SHA3-512", "SHAKE256"], 2, C.HASHES,
     [L("G must output two 32-byte values at once.", "Το G πρέπει να βγάζει δύο τιμές των 32 bytes μαζί."),
      L("64 bytes of fixed output.", "64 bytes σταθερής εξόδου.")],
     L("G = SHA3-512 gives (ρ, σ) and (K, r). H = SHA3-256, J = SHAKE256.",
       "G = SHA3-512 δίνει (ρ, σ) και (K, r). H = SHA3-256, J = SHAKE256.")),

btns("ha-reject", S_FIPS,
     L("Decapsulation re-encrypts and gets c′ ≠ c. What does it return?", "Η αποσυσκευασία ξανακρυπτογραφεί και παίρνει c′ ≠ c. Τι επιστρέφει;"),
     [L("An error code", "Κωδικό σφάλματος"), L("K̄ = J(z ‖ c), a pseudo-random key", "K̄ = J(z ‖ c), ένα ψευδοτυχαίο κλειδί"),
      L("An all-zero key", "Ένα κλειδί με όλα μηδέν"), L("The decrypted m′", "Το αποκρυπτογραφημένο m′")], 1, C.FO,
     [L("An error would tell the attacker their tampering was noticed.", "Ένα σφάλμα θα έλεγε στον επιτιθέμενο ότι η παρέμβαση έγινε αντιληπτή."),
      L("It is called implicit rejection.", "Λέγεται implicit rejection.")],
     L("Implicit rejection: a key derived from the secret z and the ciphertext, indistinguishable from a real one.",
       "Implicit rejection: ένα κλειδί από το μυστικό z και το κρυπτογράφημα, που δεν ξεχωρίζει από πραγματικό.")),

btns("ha-sizes", S_FIPS,
     L("ML-KEM-768: encapsulation key and ciphertext sizes?", "ML-KEM-768: μεγέθη κλειδιού ενθυλάκωσης και κρυπτογραφήματος;"),
     ["800 / 768", "1184 / 1088", "1568 / 1568", "1088 / 1184"], 1, C.SIZES,
     [L("k = 3, dᵤ = 10, dᵥ = 4.", "k = 3, dᵤ = 10, dᵥ = 4."),
      L("ek = 384k + 32, ct = 32(k·dᵤ + dᵥ).", "ek = 384k + 32, ct = 32(k·dᵤ + dᵥ).")],
     L("384·3 + 32 = 1184 and 32·(30 + 4) = 1088.", "384·3 + 32 = 1184 και 32·(30 + 4) = 1088.")),

btns("ha-incomplete", S_NTT,
     L("Why does ML-KEM not use a full 8-layer NTT?", "Γιατί το ML-KEM δεν χρησιμοποιεί πλήρη NTT 8 στρωμάτων;"),
     [L("3329 is not prime", "Το 3329 δεν είναι πρώτος"),
      L("3329 has a primitive 256th root but no 512th, so X²⁵⁶ + 1 only splits into 128 quadratics",
        "Το 3329 έχει πρωταρχική 256η ρίζα αλλά όχι 512η, άρα το X²⁵⁶ + 1 σπάει μόνο σε 128 τετραγωνικά"),
      L("A full NTT would be slower", "Μια πλήρης NTT θα ήταν πιο αργή"),
      L("FIPS 203 forbids it for side-channel reasons", "Το FIPS 203 το απαγορεύει για λόγους side-channel")], 1, C.NTT_REAL,
     [L("A negacyclic NTT of length n needs a root of order 2n.", "Μια negacyclic NTT μήκους n χρειάζεται ρίζα τάξης 2n."),
      L("Does 512 divide 3329 − 1 = 3328?", "Διαιρεί το 512 το 3329 − 1 = 3328;")],
     L("3328 = 2⁸·13, so roots of order up to 256 exist (ζ = 17). That limits the NTT to 7 layers.",
       "3328 = 2⁸·13, άρα υπάρχουν ρίζες τάξης έως 256 (ζ = 17). Αυτό περιορίζει την NTT σε 7 στρώματα.")),

btns("ha-gen-a", S_FIPS,
     L("How is entry A[i][j] produced?", "Πώς παράγεται το στοιχείο A[i][j];"),
     [L("SHAKE256 output fed to CBD", "Έξοδος SHAKE256 που περνά από CBD"),
      L("SHAKE128(ρ ‖ j ‖ i), keeping 12-bit values < q (rejection sampling), already in the NTT domain",
        "SHAKE128(ρ ‖ j ‖ i), κρατώντας τιμές 12 bits < q (δειγματοληψία με απόρριψη), ήδη στο πεδίο NTT"),
      L("SHA3-512 of ρ, reduced mod q", "SHA3-512 του ρ, ανηγμένο mod q"),
      L("AES-CTR keyed with ρ", "AES-CTR με κλειδί το ρ")], 1, C.HASHES,
     [L("A is public and must be uniform, not small.", "Ο A είναι δημόσιος και πρέπει να είναι ομοιόμορφος, όχι μικρός."),
      L("An XOF, with values ≥ q thrown away.", "Ένα XOF, με απόρριψη των τιμών ≥ q.")],
     L("Rejection sampling keeps the distribution exactly uniform. Note the byte order ρ ‖ j ‖ i.",
       "Η δειγματοληψία με απόρριψη κρατά την κατανομή ακριβώς ομοιόμορφη. Πρόσεξε τη σειρά ρ ‖ j ‖ i.")),

btns("ha-compress", S_ENC,
     L("Why are u and v compressed?", "Γιατί συμπιέζονται τα u και v;"),
     [L("To add security", "Για επιπλέον ασφάλεια"),
      L("To shrink the ciphertext; the rounding error is small enough to tolerate", "Για να μικρύνει το κρυπτογράφημα· το σφάλμα στρογγύλευσης είναι αρκετά μικρό"),
      L("To hide the message", "Για να κρυφτεί το μήνυμα"),
      L("The NTT requires it", "Το απαιτεί η NTT")], 1, C.COMPRESS,
     [L("Count bytes: 12 bits per coefficient versus 10 or 4.", "Μέτρα bytes: 12 bits ανά συντελεστή έναντι 10 ή 4."),
      L("The low bits are mostly noise anyway.", "Τα χαμηλά bits είναι ούτως ή άλλως κυρίως θόρυβος.")],
     L("Compression is lossy but cheap: it adds a bounded error that the q/4 budget absorbs.",
       "Η συμπίεση έχει απώλειες αλλά είναι φθηνή: προσθέτει φραγμένο σφάλμα που απορροφά το περιθώριο q/4.")),

gaps("ha-g-bitrev", S_NTT,
     L("Complete the bit-reversal permutation.", "Συμπλήρωσε τη μετάθεση αντεστραμμένων bits."),
     "python", """
def bit_reverse_permute(a):
    n = len(a); bits = n.bit_length() - 1; r = list(a)
    for i in range(n):
        j = int(format(i, f"0{bits}b")[[0]], 2)
        if [[1]]:
            r[i], r[j] = r[j], r[i]
    return r
""",
     [choice(["[::-1]", "[1:]", "[::2]"], 0, "bitrev",
             [L("Write i in binary and read it backwards.", "Γράψε το i σε δυαδικό και διάβασέ το ανάποδα."),
              L("Python reverses a string with a step of −1.", "Η Python αντιστρέφει string με βήμα −1.")]),
      choice(["j > i", "j != i", "True"], 0, "bitrev",
             [L("Each pair (i, j) is visited twice: once at i, once at j.", "Κάθε ζεύγος (i, j) το συναντάμε δύο φορές: στο i και στο j."),
              L("Swap only on one of the two visits.", "Αντάλλαξε μόνο στη μία από τις δύο επισκέψεις.")])],
     C.BITREV,
     L("Reverse the bits, and swap only when j > i; swapping on both visits puts everything back.",
       "Αντιστρέφουμε τα bits και ανταλλάσσουμε μόνο όταν j > i· αν ανταλλάξουμε και στις δύο επισκέψεις όλα γυρίζουν πίσω."),
     check="assert bit_reverse_permute(list(range(8))) == [0, 4, 2, 6, 1, 5, 3, 7]"),

gaps("ha-g-ntt-loop", S_NTT,
     L("Complete the iterative (Cooley–Tukey) NTT loop.", "Συμπλήρωσε τον επαναληπτικό βρόχο NTT (Cooley–Tukey)."),
     "python", """
def ntt_cyclic(poly, roots, q):
    n = len(poly); a = bit_reverse_permute(poly); length = 2
    while length <= n:
        step = n // length
        for start in range(0, n, length):
            for j in range(length // 2):
                f, s = start + j, start + j + length // 2
                a[f], a[s] = butterfly(a[f], a[s], [[0]], q)
        length [[1]]
    return a
""",
     [choice(["roots[j * step]", "roots[j]", "roots[step]", "roots[f]"], 0, "roots",
             [L("Small blocks use few distinct roots; the last layer uses all of them.", "Τα μικρά μπλοκ χρησιμοποιούν λίγες ρίζες· το τελευταίο στρώμα όλες."),
              L("A block of length L uses the L-th roots: ω^(n/L · j).", "Ένα μπλοκ μήκους L χρησιμοποιεί τις L-οστές ρίζες: ω^(n/L · j).")]),
      choice(["<<= 1", "+= 1", "*= 4"], 0, "ntt_layers",
             [L("There are log₂ n layers.", "Υπάρχουν log₂ n στρώματα."),
              L("Block length goes 2, 4, 8.", "Το μήκος του μπλοκ πάει 2, 4, 8.")])],
     C.NTT,
     L("Each layer doubles the block length and uses roots ω^(step·j). That is 3 layers for n = 8.",
       "Κάθε στρώμα διπλασιάζει το μήκος μπλοκ και χρησιμοποιεί ρίζες ω^(step·j). Δηλαδή 3 στρώματα για n = 8."),
     check=("for a in ([1,2,3,4,5,6,7,8], [16,0,3,1,0,2,9,15]):\n"
            "    assert ntt_cyclic(twist(a), ROOTS, 17) == ntt(a)")),

gaps("ha-g-roots", S_NTT,
     L("Derive ψ and ω for the toy from the generator 3.", "Παράγαγε τα ψ και ω του toy από τον γεννήτορα 3."),
     "python", """
psi = modpow(3, (Q - 1) // ([[0]]), Q)   # needs order 2n for X^n + 1
omega = [[1]]
""",
     [text(["2 * N", "16", "N * 2", "2 * 8"], "roots",
           [L("A negacyclic NTT of length n needs a root of order 2n.", "Μια negacyclic NTT μήκους n χρειάζεται ρίζα τάξης 2n."),
            L("3 has order 16; raise it to (q − 1)/(desired order).", "Το 3 έχει τάξη 16· ύψωσέ το σε (q − 1)/(επιθυμητή τάξη).")], width=7),
      choice(["psi * psi % Q", "psi * 2 % Q", "modpow(psi, N, Q)"], 0, "roots",
             [L("ω must have order n = 8.", "Το ω πρέπει να έχει τάξη n = 8."),
              L("If ψ has order 16, which power of it has order 8?", "Αν το ψ έχει τάξη 16, ποια δύναμή του έχει τάξη 8;")])],
     C.TWIST,
     L("ψ = 3^((17−1)/16) = 3 and ω = ψ² = 9.", "ψ = 3^((17−1)/16) = 3 και ω = ψ² = 9."),
     check="assert psi == 3 and omega == 9"),

gaps("ha-g-ninv-real", S_NTT,
     L("Real ML-KEM: what constant scales the 7-layer INTT?", "Πραγματικό ML-KEM: ποια σταθερά κλιμακώνει την INTT των 7 στρωμάτων;"),
     "python", """
q = 3329
n_inv_real = [[0]]       # undoes the 128 pairs of the incomplete NTT
""",
     [text(["3303", "pow(128, -1, q)", "pow(128, q - 2, q)", "modpow(128, q - 2, q)", "pow(128, -1, 3329)"], "n_inv",
           [L("7 layers act on 128 blocks, not 256 points.", "Τα 7 στρώματα δρουν σε 128 μπλοκ, όχι σε 256 σημεία."),
            L("Find x with 128·x ≡ 1 (mod 3329); Fermat gives x = 128^(q−2).", "Βρες x με 128·x ≡ 1 (mod 3329)· ο Fermat δίνει x = 128^(q−2).")], width=8)],
     C.INTT,
     L("128⁻¹ mod 3329 = 3303. Using 256⁻¹ = 3316 here is a classic bug.", "128⁻¹ mod 3329 = 3303. Η χρήση του 256⁻¹ = 3316 εδώ είναι κλασικό bug."),
     check="assert 128 * n_inv_real % q == 1 and 0 < n_inv_real < q"),

gaps("ha-g-u", S_ENC,
     L("Complete u = INTT(Âᵀ·r̂) + e₁.", "Συμπλήρωσε το u = INTT(Âᵀ·r̂) + e₁."),
     "python", """
def encrypt_u(A_hat, r, e1, q):
    r_hat = [ntt(p, q) for p in r]
    At = [[[[0]] for j in range(K)] for i in range(K)]
    return [poly_add(intt(x, q), e, q) for x, e in zip(matvec_ntt(At, r_hat, q), e1)]
""",
     [choice(["A_hat[j][i]", "A_hat[i][j]", "A_hat[i][i]"], 0, "transpose",
             [L("Encryption uses the transpose of the key-generation matrix.", "Η κρυπτογράφηση χρησιμοποιεί τον ανάστροφο του πίνακα της δημιουργίας κλειδιών."),
              L("Transpose swaps row and column.", "Ο ανάστροφος ανταλλάσσει γραμμή και στήλη.")])],
     C.ENCRYPT,
     L("Aᵀ makes sᵀ·u contain sᵀAᵀr, the same term as tᵀr in v, so it cancels.",
       "Ο Aᵀ κάνει το sᵀ·u να περιέχει το sᵀAᵀr, ίδιο όρο με το tᵀr στο v, οπότε αλληλοαναιρείται."),
     check=("t_hat, s_hat = keygen(A_HAT, S, E)\n"
            "u_ref, _ = encrypt(A_HAT, t_hat, R, E1, E2, MSG)\n"
            "assert encrypt_u(A_HAT, R, E1, 17) == u_ref")),

gaps("ha-g-v", S_ENC,
     L("Complete v = INTT(t̂ᵀ·r̂) + e₂ + encode(m).", "Συμπλήρωσε το v = INTT(t̂ᵀ·r̂) + e₂ + encode(m)."),
     "python", """
def encrypt_v(t_hat, r_hat, e2, msg, q):
    vp = intt(inner_ntt([[0]], r_hat, q), q)
    return poly_add(poly_add(vp, e2, q), [[1]], q)
""",
     [choice(["t_hat", "r_hat", "e2"], 0, "encode",
             [L("v is built from the public key.", "Το v φτιάχνεται από το δημόσιο κλειδί."),
              L("Inner product of t̂ with r̂.", "Εσωτερικό γινόμενο του t̂ με το r̂.")]),
      choice(["encode_message(msg, q)", "msg", "[b * q for b in msg]", "[b * (q // 4) for b in msg]"], 0, "encode",
             [L("A bit of 1 must be far from 0 on the circle.", "Ένα bit 1 πρέπει να είναι μακριά από το 0 στον κύκλο."),
              L("bit · ⌊q/2⌋.", "bit · ⌊q/2⌋.")])],
     C.ENCRYPT,
     L("v hides the message under tᵀr + e₂. Encoding at ⌊q/2⌋ leaves a q/4 margin either side.",
       "Το v κρύβει το μήνυμα κάτω από tᵀr + e₂. Η κωδικοποίηση στο ⌊q/2⌋ αφήνει περιθώριο q/4 από κάθε πλευρά."),
     check=("t_hat, s_hat = keygen(A_HAT, S, E)\n"
            "_, v_ref = encrypt(A_HAT, t_hat, R, E1, E2, MSG)\n"
            "assert encrypt_v(t_hat, [ntt(p) for p in R], E2, MSG, 17) == v_ref")),

gaps("ha-g-budget", S_ENC,
     L("Complete the noise-budget test.", "Συμπλήρωσε τον έλεγχο του περιθωρίου θορύβου."),
     "python", """
def within_budget(noise, q):
    return all(abs(x) < [[0]] for x in noise)
""",
     [text(["q / 4", "q * 0.25", "0.25 * q"], "noise",
           [L("Bit 0 sits at 0 and bit 1 at ⌊q/2⌋.", "Το bit 0 βρίσκεται στο 0 και το bit 1 στο ⌊q/2⌋."),
            L("The decision boundary is halfway between them: a quarter of the modulus.", "Το όριο απόφασης είναι στη μέση: ένα τέταρτο του modulus.")], width=7)],
     C.DECRYPT,
     L("Noise below q/4 still rounds to the right encoding; at q/4 or more it can cross over.",
       "Θόρυβος κάτω από q/4 στρογγυλεύεται ακόμη στη σωστή κωδικοποίηση· από q/4 και πάνω μπορεί να περάσει απέναντι."),
     check=("assert within_budget([4, -4, 0], 17) and within_budget([4.2], 17)\n"
            "assert not within_budget([5], 17) and not within_budget([-4.3], 17)\n"
            "assert within_budget([832], 3329) and not within_budget([833], 3329)")),

gaps("ha-g-compress", S_ENC,
     L("Complete Compress_d for q = 3329.", "Συμπλήρωσε το Compress_d για q = 3329."),
     "python", """
def compress(x, d, q=3329):
    return ([[0]]) % (1 << d)

def decompress(y, d, q=3329):
    return (q * y + (1 << (d - 1))) >> d
""",
     [choice(["((x << d) + q // 2) // q", "(x << d) // q", "x >> d", "(x * q) >> d"], 0, "compress",
             [L("Scale x from [0, q) to [0, 2ᵈ).", "Κλιμάκωσε το x από [0, q) σε [0, 2ᵈ)."),
              L("Round, do not truncate: add half the divisor before dividing.", "Στρογγύλευσε, μην αποκόψεις: πρόσθεσε το μισό του διαιρέτη πριν διαιρέσεις.")])],
     C.COMPRESS,
     L("⌈2ᵈ·x/q⌋ mod 2ᵈ, computed with integers by adding q/2 before dividing. Truncation doubles the error.",
       "⌈2ᵈ·x/q⌋ mod 2ᵈ, με ακέραιους προσθέτοντας q/2 πριν τη διαίρεση. Η αποκοπή διπλασιάζει το σφάλμα."),
     check=("from fractions import Fraction\n"
            "import math\n"
            "for d in (1, 4, 10, 11):\n"
            "    for x in range(3329):\n"
            "        assert compress(x, d) == math.floor(Fraction(2 ** d * x, 3329) + Fraction(1, 2)) % 2 ** d")),
]
