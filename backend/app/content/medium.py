"""
Level 3: Medium. Harder hand computations, then the first code: every gap is
a multiple choice on a Kyber idea, never on a variable name. Each distractor
is a real mistake and is proven wrong by running the check.
"""
from app.content import cards as C
from app.content.schema import L, btns, choice, duo, gaps

S_CBD = L("Noise sampling", "Δειγματοληψία θορύβου")
S_NTT = L("NTT", "NTT")
S_KG = L("Key generation", "Δημιουργία κλειδιών")
S_DEC = L("Decryption", "Αποκρυπτογράφηση")

QUESTIONS = [
duo("me-cbd-hi", S_CBD,
    L("Byte <code>0x30</code> = 00110000. For coeff[1] use bits 4–7: b₀=1, b₁=1, b₂=0, b₃=0. What is coeff[1]?",
      "Byte <code>0x30</code> = 00110000. Για το coeff[1] χρησιμοποίησε τα bits 4–7: b₀=1, b₁=1, b₂=0, b₃=0. Πόσο είναι το coeff[1];"),
    "coeff[1] =", ["2"], C.CBD,
    [L("One byte gives two coefficients; the second uses the high nibble.", "Ένα byte δίνει δύο συντελεστές· ο δεύτερος χρησιμοποιεί το ανώτερο nibble."),
     L("(b₀ + b₁) − (b₂ + b₃) on bits 4–7.", "(b₀ + b₁) − (b₂ + b₃) στα bits 4–7.")],
    L("(1 + 1) − (0 + 0) = 2.", "(1 + 1) − (0 + 0) = 2.")),

duo("me-cbd-stored", S_CBD,
    L("Byte <code>0xC0</code> = 11000000. coeff[1] uses bits 4–7 = 0, 0, 1, 1. What is <b>stored</b> mod 17?",
      "Byte <code>0xC0</code> = 11000000. Το coeff[1] χρησιμοποιεί τα bits 4–7 = 0, 0, 1, 1. Τι <b>αποθηκεύεται</b> mod 17;"),
    "coeff[1] =", ["15"], C.CBD,
    [L("The raw value is negative.", "Η ακατέργαστη τιμή είναι αρνητική."),
     L("(0 + 0) − (1 + 1) = −2, then reduce.", "(0 + 0) − (1 + 1) = −2, μετά ανάγαγε.")],
    L("−2 + 17 = 15.", "−2 + 17 = 15.")),

duo("me-twist", S_NTT,
    L("Before the toy NTT, coefficient i is multiplied by ψⁱ (ψ = 3). With a₂ = 5, what is the twisted a₂?",
      "Πριν την NTT του toy, ο συντελεστής i πολλαπλασιάζεται με ψⁱ (ψ = 3). Με a₂ = 5, πόσο είναι το a₂ μετά το twist;"),
    "5·ψ² mod 17 =", ["11"], C.TWIST,
    [L("ψ² = 9.", "ψ² = 9."),
     L("5·9 = 45; reduce mod 17.", "5·9 = 45· ανάγαγε mod 17.")],
    L("45 = 2·17 + 11. This twist is what makes the NTT respect X⁸ + 1 instead of X⁸ − 1.",
      "45 = 2·17 + 11. Αυτό το twist κάνει την NTT να σέβεται το X⁸ + 1 αντί για X⁸ − 1.")),

duo("me-that", S_KG,
    L("One coefficient of t̂[0]: Â[0][0] = 11, ŝ[0] = 1, Â[0][1] = 6, ŝ[1] = 8, ê[0] = 1. Compute it.",
      "Ένας συντελεστής του t̂[0]: Â[0][0] = 11, ŝ[0] = 1, Â[0][1] = 6, ŝ[1] = 8, ê[0] = 1. Υπολόγισέ τον."),
    "t̂[0] =", ["9"], C.KEYGEN,
    [L("Row 0 of Â times ŝ, plus ê.", "Γραμμή 0 του Â επί ŝ, συν ê."),
     L("11·1 + 6·8 + 1 = 60; reduce mod 17.", "11·1 + 6·8 + 1 = 60· ανάγαγε mod 17.")],
    L("60 = 3·17 + 9.", "60 = 3·17 + 9.")),

duo("me-modpow", S_NTT,
    L("Compute <b>3⁸ mod 17</b> by repeated squaring.", "Υπολόγισε <b>3⁸ mod 17</b> με διαδοχικά τετράγωνα."),
    "3⁸ mod 17 =", ["16"], C.ROOTS,
    [L("3² = 9, 3⁴ = 9², 3⁸ = (3⁴)².", "3² = 9, 3⁴ = 9², 3⁸ = (3⁴)²."),
     L("3⁴ = 81 ≡ 13, then 13² = 169.", "3⁴ = 81 ≡ 13, μετά 13² = 169.")],
    L("169 = 9·17 + 16, so 3⁸ ≡ −1. That is why 3 has order 16 and can be ψ.",
      "169 = 9·17 + 16, άρα 3⁸ ≡ −1. Γι' αυτό το 3 έχει τάξη 16 και μπορεί να είναι ψ.")),

btns("me-cbd-range", S_CBD,
     L("CBD with η = 2 produces values in which set?", "Το CBD με η = 2 δίνει τιμές σε ποιο σύνολο;"),
     ["{0, …, 16}", "{−2, −1, 0, 1, 2}", "{0, 1}", "{−8, …, 8}"], 1, C.CBD,
     [L("Each pair sum is between 0 and 2.", "Κάθε άθροισμα ζεύγους είναι μεταξύ 0 και 2."),
      L("Largest is 2 − 0, smallest is 0 − 2.", "Το μέγιστο είναι 2 − 0, το ελάχιστο 0 − 2.")],
     L("{−2, …, 2}, centred on 0, with 0 the most likely value.", "{−2, …, 2}, κεντραρισμένο στο 0, με το 0 πιο πιθανό.")),

btns("me-toy-layers", S_NTT,
     L("How many butterfly layers does the toy NTT (n = 8) have?", "Πόσα στρώματα πεταλούδων έχει η NTT του toy (n = 8);"),
     ["8", "2", "3", "4"], 2, C.NTT,
     [L("Each layer doubles the block length.", "Κάθε στρώμα διπλασιάζει το μήκος του μπλοκ."),
      L("2 → 4 → 8.", "2 → 4 → 8.")],
     L("log₂ 8 = 3 layers.", "log₂ 8 = 3 στρώματα.")),

btns("me-real-layers", S_NTT,
     L("And the NTT in real ML-KEM (n = 256, q = 3329)?", "Και η NTT στο πραγματικό ML-KEM (n = 256, q = 3329);"),
     [L("8 layers (log₂ 256)", "8 στρώματα (log₂ 256)"), L("7 layers, stopping at 128 degree-1 pairs", "7 στρώματα, σταματά σε 128 ζεύγη βαθμού 1"),
      L("9 layers", "9 στρώματα"), L("128 layers", "128 στρώματα")], 1, C.NTT_REAL,
     [L("A full negacyclic NTT would need a primitive 512th root of unity.", "Μια πλήρης negacyclic NTT θα χρειαζόταν πρωταρχική 512η ρίζα της μονάδας."),
      L("3329 − 1 = 2⁸·13 has only eight factors of 2.", "Το 3329 − 1 = 2⁸·13 έχει μόνο οκτώ παράγοντες 2.")],
     L("7 layers. The last step is done by basemul on pairs, not by an 8th layer.",
       "7 στρώματα. Το τελευταίο βήμα γίνεται με basemul σε ζεύγη, όχι με 8ο στρώμα.")),

btns("me-encode-vec", S_KG,
     L("MSG = [1, 0, 1, 0, 1, 0, 1, 0], q = 17. What is the encoded vector?",
       "MSG = [1, 0, 1, 0, 1, 0, 1, 0], q = 17. Ποιο είναι το κωδικοποιημένο διάνυσμα;"),
     ["[1,0,1,0,1,0,1,0]", "[17,0,17,0,17,0,17,0]", "[8,8,8,8,8,8,8,8]", "[8,0,8,0,8,0,8,0]"], 3, C.ENCRYPT,
     [L("Each bit is encoded on its own.", "Κάθε bit κωδικοποιείται χωριστά."),
      L("bit · ⌊q/2⌋.", "bit · ⌊q/2⌋.")],
     L("1 → 8, 0 → 0.", "1 → 8, 0 → 0.")),

btns("me-cancel", S_DEC,
     L("What cancels in w = v − sᵀ·u?", "Τι αλληλοαναιρείται στο w = v − sᵀ·u;"),
     [L("The message", "Το μήνυμα"), L("The error e₂", "Το σφάλμα e₂"),
      L("The large term sᵀ·Aᵀ·r, present in both v and sᵀ·u", "Ο μεγάλος όρος sᵀ·Aᵀ·r, που υπάρχει και στο v και στο sᵀ·u"),
      L("The matrix A itself", "Ο ίδιος ο πίνακας A")], 2, C.ENCRYPT,
     [L("Write v using t = A·s + e.", "Γράψε το v με t = A·s + e."),
      L("tᵀ·r = sᵀ·Aᵀ·r + eᵀ·r.", "tᵀ·r = sᵀ·Aᵀ·r + eᵀ·r.")],
     L("v − sᵀu = m·⌊q/2⌋ + (eᵀr + e₂ − sᵀe₁): only small noise remains next to the message.",
       "v − sᵀu = m·⌊q/2⌋ + (eᵀr + e₂ − sᵀe₁): μένει μόνο μικρός θόρυβος δίπλα στο μήνυμα.")),

gaps("me-g-butterfly", S_NTT,
     L("Complete one NTT butterfly.", "Συμπλήρωσε μία πεταλούδα NTT."),
     "python", """
def butterfly(u, v, w, q):
    t = [[0]]
    return (u + t) % q, [[1]]
""",
     [choice(["v * w % q", "u * w % q", "(u + v) * w % q", "v + w"], 0, "butterfly",
             [L("Only the second input is multiplied by the root.", "Μόνο η δεύτερη είσοδος πολλαπλασιάζεται με τη ρίζα."),
              L("t = v·w mod q.", "t = v·w mod q.")]),
      choice(["(u - t) % q", "(t - u) % q", "u - t", "(u + t) % q"], 0, "butterfly",
             [L("The second output is the 'minus' side of the butterfly.", "Η δεύτερη έξοδος είναι η πλευρά «μείον» της πεταλούδας."),
              L("It must stay in {0, …, q−1} even when u < t.", "Πρέπει να μένει στο {0, …, q−1} ακόμη κι όταν u < t.")])],
     C.BUTTERFLY,
     L("u′ = u + vw and v′ = u − vw, both mod q. Forgetting % q on the subtraction leaves negative numbers.",
       "u′ = u + vw και v′ = u − vw, και τα δύο mod q. Αν ξεχάσεις το % q στην αφαίρεση μένουν αρνητικοί αριθμοί."),
     check="assert butterfly(3, 1, 9, 17) == (12, 11)\nassert butterfly(2, 3, 9, 17) == (12, 9)"),

gaps("me-g-cbd", S_CBD,
     L("Complete the η = 2 CBD sampler.", "Συμπλήρωσε τον δειγματολήπτη CBD με η = 2."),
     "python", """
def cbd_eta2(byte_list, q):
    out = []
    for byte_val in byte_list:
        bits = [(byte_val >> i) & 1 for i in range(8)]
        for pair in range(2):
            b0, b1, b2, b3 = bits[pair * 4 : pair * 4 + 4]
            out.append([[0]])
    return out
""",
     [choice(["((b0 + b1) - (b2 + b3)) % q", "(b0 + b1 + b2 + b3) % q",
              "((b0 - b1) + (b2 - b3)) % q", "(b0 + b1) - (b2 + b3)"], 0, "cbd",
             [L("Two bits count up, two bits count down.", "Δύο bits μετρούν προς τα πάνω, δύο προς τα κάτω."),
              L("(b₀ + b₁) − (b₂ + b₃), stored mod q.", "(b₀ + b₁) − (b₂ + b₃), αποθηκευμένο mod q.")])],
     C.CBD,
     L("The difference of two pair sums is centred on 0. Without % q a −2 would be stored as −2 instead of 15.",
       "Η διαφορά δύο αθροισμάτων ζευγών κεντράρεται στο 0. Χωρίς % q το −2 θα αποθηκευόταν ως −2 αντί για 15."),
     check="assert cbd_eta2([0x0C, 0x30, 0xF0], 17) == [15, 0, 0, 2, 0, 0]"),

gaps("me-g-twist", S_NTT,
     L("The toy NTT must multiply mod X⁸ + 1. Complete the twist.", "Η NTT του toy πρέπει να πολλαπλασιάζει mod X⁸ + 1. Συμπλήρωσε το twist."),
     "python", """
def ntt(poly, q):
    twisted = [c * [[0]] % q for i, c in enumerate(poly)]
    return ntt_cyclic(twisted, ROOTS, q)
""",
     [choice(["modpow(PSI, i, q)", "modpow(OMEGA, i, q)", "PSI", "modpow(PSI, 2 * i, q)"], 0, "twist",
             [L("The twist uses the 16th root, not the 8th.", "Το twist χρησιμοποιεί τη 16η ρίζα, όχι την 8η."),
              L("Coefficient i is scaled by ψⁱ.", "Ο συντελεστής i κλιμακώνεται με ψⁱ.")])],
     C.TWIST,
     L("Scaling a_i by ψⁱ (ψ² = ω) turns cyclic convolution into negacyclic. Using ωⁱ would compute a product mod X⁸ − 1.",
       "Η κλιμάκωση του a_i με ψⁱ (ψ² = ω) κάνει την κυκλική συνέλιξη negacyclic. Με ωⁱ θα υπολογιζόταν γινόμενο mod X⁸ − 1."),
     check=("for a, b in [([1,2,3,4,5,6,7,8], [8,7,6,5,4,3,2,1]), ([0,1,0,0,0,0,0,0], [0,0,0,0,0,0,0,1])]:\n"
            "    assert intt(pointwise_mul(ntt(a, 17), ntt(b, 17))) == schoolbook_mul(a, b)")),

gaps("me-g-intt", S_NTT,
     L("Complete the scaling at the end of the toy INTT.", "Συμπλήρωσε την κλιμάκωση στο τέλος της INTT του toy."),
     "python", """
def intt(poly_hat, q):
    a = ntt_cyclic(poly_hat, INV_ROOTS, q)
    return [c * [[0]] * modpow(PSI_INV, i, q) % q for i, c in enumerate(a)]
""",
     [choice(["N_INV", "N", "Q - 1", "OMEGA_INV"], 0, "n_inv",
             [L("Running the transform forward and back multiplies everything by n.", "Ο μετασχηματισμός μπρος-πίσω πολλαπλασιάζει τα πάντα με n."),
              L("Undo it with n⁻¹ = 15.", "Αναίρεσέ το με n⁻¹ = 15.")])],
     C.INTT,
     L("Multiply by n⁻¹ (and untwist by ψ⁻ⁱ). In ML-KEM the constant is 128⁻¹ = 3303.",
       "Πολλαπλασιάζουμε με n⁻¹ (και αναιρούμε το twist με ψ⁻ⁱ). Στο ML-KEM η σταθερά είναι 128⁻¹ = 3303."),
     check="for a in ([1,2,3,4,5,6,7,8], [16,0,0,1,0,2,0,15]):\n    assert intt(ntt(a, 17), 17) == a"),

gaps("me-g-keygen", S_KG,
     L("Complete t̂ = Â·ŝ + ê.", "Συμπλήρωσε το t̂ = Â·ŝ + ê."),
     "python", """
def keygen_t(A_hat, s_hat, e_hat, q):
    t_hat = []
    for row in range(len(A_hat)):
        acc = [0] * len(s_hat[0])
        for col in range(len(A_hat)):
            acc = poly_add(acc, pointwise_mul([[0]], s_hat[col], q), q)
        t_hat.append([[1]])
    return t_hat
""",
     [choice(["A_hat[row][col]", "A_hat[col][row]", "A_hat[row][row]"], 0, "matrix",
             [L("Matrix times vector: row of the matrix, entry of the vector.", "Πίνακας επί διάνυσμα: γραμμή του πίνακα, στοιχείο του διανύσματος."),
              L("Entry (row, col) multiplies ŝ[col].", "Το στοιχείο (row, col) πολλαπλασιάζει το ŝ[col].")]),
      choice(["poly_add(acc, e_hat[row], q)", "poly_sub(acc, e_hat[row], q)", "acc", "poly_add(acc, s_hat[row], q)"], 0, "noise",
             [L("Without the error, t̂ would reveal ŝ by linear algebra.", "Χωρίς το σφάλμα, το t̂ θα αποκάλυπτε το ŝ με γραμμική άλγεβρα."),
              L("+ ê[row].", "+ ê[row].")])],
     C.KEYGEN,
     L("t̂[row] = Σ Â[row][col]⊙ŝ[col] + ê[row]. The added error is the 'E' in MLWE.",
       "t̂[row] = Σ Â[row][col]⊙ŝ[col] + ê[row]. Το σφάλμα που προστίθεται είναι το «E» του MLWE."),
     check=("t_ref, s_hat = keygen(A_HAT, S, E)\n"
            "assert keygen_t(A_HAT, s_hat, [ntt(e) for e in E], 17) == t_ref")),

gaps("me-g-decrypt", S_DEC,
     L("Complete decryption.", "Συμπλήρωσε την αποκρυπτογράφηση."),
     "python", """
def decrypt(s_hat, u, v, q):
    u_hat = [[[0]] for p in u]
    w = poly_sub([[1]], intt(inner_ntt(s_hat, u_hat, q), q), q)
    return [decode_bit(c, q) for c in w]
""",
     [choice(["ntt(p, q)", "intt(p, q)", "p"], 0, "ntt_layers",
             [L("ŝ is stored in the NTT domain; u arrives in normal form.", "Το ŝ είναι αποθηκευμένο στο πεδίο NTT· το u φτάνει σε κανονική μορφή."),
              L("Bring u into the same domain before multiplying.", "Φέρε το u στο ίδιο πεδίο πριν τον πολλαπλασιασμό.")]),
      choice(["v", "u[0]", "encode_message(v)"], 0, "decode",
             [L("Which part of the ciphertext carries the message?", "Ποιο μέρος του κρυπτογραφήματος μεταφέρει το μήνυμα;"),
              L("w = v − sᵀ·u.", "w = v − sᵀ·u.")])],
     C.DECRYPT,
     L("NTT(u), multiply by ŝ, INTT back, subtract from v. Mixing domains gives garbage.",
       "NTT(u), πολλαπλασιασμός με ŝ, INTT πίσω, αφαίρεση από το v. Η ανάμειξη πεδίων δίνει σκουπίδια."),
     check=("t_hat, s_hat = keygen(A_HAT, S, E)\n"
            "u, v = encrypt(A_HAT, t_hat, R, E1, E2, MSG)\n"
            "assert decrypt(s_hat, u, v, 17) == MSG")),

gaps("me-g-decode", S_DEC,
     L("Complete the bit decoder.", "Συμπλήρωσε τον αποκωδικοποιητή bit."),
     "python", """
def decode_bit(c, q):
    half = [[0]]
    d0 = min(c, q - c)
    dq2 = min(abs(c - half), q - abs(c - half))
    return 1 if [[1]] else 0
""",
     [choice(["q // 2", "q // 4", "q", "0"], 0, "decode",
             [L("Where was bit 1 placed by the encoder?", "Πού τοποθέτησε ο κωδικοποιητής το bit 1;"),
              L("⌊q/2⌋.", "⌊q/2⌋.")]),
      choice(["dq2 < d0", "d0 < dq2", "c > half", "dq2 == 0"], 0, "decode",
             [L("Pick the encoding that is closer.", "Διάλεξε την κωδικοποίηση που είναι πιο κοντά."),
              L("Bit 1 when the distance to q/2 is smaller than the distance to 0.", "Bit 1 όταν η απόσταση από q/2 είναι μικρότερη από την απόσταση από 0.")])],
     C.DECRYPT,
     L("Compare circular distances to 0 and ⌊q/2⌋. A plain threshold like c > q/2 fails for values just below 8.",
       "Συγκρίνουμε κυκλικές αποστάσεις από 0 και ⌊q/2⌋. Ένα απλό κατώφλι όπως c > q/2 αποτυγχάνει για τιμές λίγο κάτω από 8."),
     check="assert [decode_bit(c, 17) for c in [9, 1, 8, 8, 0, 16, 9, 0, 3, 13]] == [1, 0, 1, 1, 0, 0, 1, 0, 0, 0]"),
]
