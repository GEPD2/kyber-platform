"""
Shared theory cards. One sentence of what, one formula, one worked example
with the toy numbers (q=17, n=8 unless stated), and why ML-KEM needs it.
Every number here is recomputed by tests/test_content.py.
"""
from app.content.schema import L, card

MOD = card(
    L("Reduction mod q", "Αναγωγή mod q"),
    L("Every Kyber coefficient lives in Z_q = {0, …, q−1}; after each operation take the remainder.",
      "Κάθε συντελεστής του Kyber ζει στο Z_q = {0, …, q−1}· μετά από κάθε πράξη κρατάμε το υπόλοιπο."),
    "x mod q = x − q·⌊x/q⌋",
    "19 mod 17 = 19 − 17 = 2",
    L("FIPS 203 uses q = 3329; keeping numbers small is what makes the arithmetic fast and exact.",
      "Το FIPS 203 χρησιμοποιεί q = 3329· οι μικροί αριθμοί κάνουν την αριθμητική γρήγορη και ακριβή."),
)

NEG = card(
    L("Negative values mod q", "Αρνητικές τιμές mod q"),
    L("A negative value is stored as its positive representative: add q once.",
      "Μια αρνητική τιμή αποθηκεύεται ως θετικός αντιπρόσωπος: προσθέτουμε q μία φορά."),
    "−x mod q = q − x   (0 < x < q)",
    "−1 mod 17 = 17 − 1 = 16",
    L("Noise coefficients are small and often negative (−2 … 2); they are stored this way.",
      "Οι συντελεστές θορύβου είναι μικροί και συχνά αρνητικοί (−2 … 2)· αποθηκεύονται έτσι."),
)

RING = card(
    L("The negacyclic ring", "Ο negacyclic δακτύλιος"),
    L("Polynomials are taken mod Xⁿ + 1, so Xⁿ wraps round to −1.",
      "Τα πολυώνυμα παίρνονται mod Xⁿ + 1, άρα το Xⁿ «τυλίγεται» σε −1."),
    "X⁸ ≡ −1  ⇒  X⁹ = X⁸·X ≡ −X",
    "3·X⁹ → −3·X ≡ 14·X  (mod 17)",
    L("ML-KEM works in Z_q[X]/(X²⁵⁶ + 1); the toy uses n = 8 so you can do it by hand.",
      "Το ML-KEM δουλεύει στο Z_q[X]/(X²⁵⁶ + 1)· το toy έχει n = 8 για να γίνεται με το χέρι."),
)

CBD = card(
    L("Centered binomial noise (CBD, η = 2)", "Κεντρικός διωνυμικός θόρυβος (CBD, η = 2)"),
    L("Take 4 random bits b₀…b₃ (read least-significant first) and subtract the two pair sums.",
      "Παίρνουμε 4 τυχαία bits b₀…b₃ (από το λιγότερο σημαντικό) και αφαιρούμε τα δύο αθροίσματα ζευγών."),
    "coeff = (b₀ + b₁) − (b₂ + b₃)   ∈ {−2, …, 2}",
    "0x0C → bits 0,0,1,1 → (0+0) − (1+1) = −2 → 15",
    L("Secret s and errors e must be small for decryption to work. ML-KEM-512 uses η₁ = 3 for s, e, r; η = 2 everywhere else.",
      "Το μυστικό s και τα σφάλματα e πρέπει να είναι μικρά για να δουλεύει η αποκρυπτογράφηση. Το ML-KEM-512 χρησιμοποιεί η₁ = 3 για s, e, r· παντού αλλού η = 2."),
)

ROOTS = card(
    L("Roots of unity mod 17", "Ρίζες της μονάδας mod 17"),
    L("ψ = 3 has order 16 and ω = ψ² = 9 has order 8: the powers of ω are the NTT evaluation points.",
      "Το ψ = 3 έχει τάξη 16 και το ω = ψ² = 9 τάξη 8: οι δυνάμεις του ω είναι τα σημεία αποτίμησης της NTT."),
    "ROOTS[k] = ωᵏ mod q",
    "ω² = 81 = 4·17 + 13 → 13",
    L("The NTT needs these roots. q = 3329 only has roots up to order 256, which is why Kyber's NTT is incomplete.",
      "Η NTT χρειάζεται αυτές τις ρίζες. Το q = 3329 έχει ρίζες μόνο ως τάξη 256· γι' αυτό η NTT του Kyber είναι ελλιπής."),
)

BUTTERFLY = card(
    L("The NTT butterfly", "Η πεταλούδα (butterfly) της NTT"),
    L("One step mixes a pair (u, v) with a root w: one output adds, the other subtracts.",
      "Ένα βήμα αναμειγνύει ένα ζεύγος (u, v) με μια ρίζα w: η μία έξοδος προσθέτει, η άλλη αφαιρεί."),
    "t = v·w mod q,  u′ = (u + t) mod q,  v′ = (u − t) mod q",
    "u=2, v=3, w=9: t = 27 mod 17 = 10, u′ = 12, v′ = −8 → 9",
    L("Every layer of the NTT is just many butterflies; Kyber runs 7 layers of them.",
      "Κάθε στρώμα της NTT είναι απλώς πολλές πεταλούδες· ο Kyber τρέχει 7 τέτοια στρώματα."),
)

NTT = card(
    L("NTT: fast polynomial multiplication", "NTT: γρήγορος πολλαπλασιασμός πολυωνύμων"),
    L("Transform both polynomials, multiply coefficient by coefficient, transform back.",
      "Μετασχηματίζουμε και τα δύο πολυώνυμα, πολλαπλασιάζουμε συντελεστή-συντελεστή, γυρίζουμε πίσω."),
    "a·b = INTT( NTT(a) ⊙ NTT(b) )",
    "toy: 3 layers for n = 8 (log₂8); twist by ψⁱ first so it matches X⁸ + 1",
    L("Schoolbook multiply costs n² steps; the NTT costs about n·log n. Kyber keys and ciphertexts are mostly polynomial products.",
      "Ο σχολικός πολλαπλασιασμός κοστίζει n² βήματα· η NTT περίπου n·log n. Τα κλειδιά και τα κρυπτοκείμενα του Kyber είναι κυρίως γινόμενα πολυωνύμων."),
)

TWIST = card(
    L("Negacyclic twist", "Negacyclic twist"),
    L("A plain NTT multiplies mod Xⁿ − 1. Multiplying coefficient i by ψⁱ first (ψ² = ω) turns it into a multiply mod Xⁿ + 1.",
      "Μια απλή NTT πολλαπλασιάζει mod Xⁿ − 1. Αν πρώτα πολλαπλασιάσουμε τον συντελεστή i με ψⁱ (ψ² = ω), γίνεται πολλαπλασιασμός mod Xⁿ + 1."),
    "NTT⁻(a) = NTT( a₀, a₁ψ, a₂ψ², … );  INTT undoes with n⁻¹·ψ⁻ⁱ",
    "a₂ = 5, ψ² = 9 → 5·9 = 45 mod 17 = 11",
    L("Kyber's ring is X²⁵⁶ + 1, so the twist (folded into the zetas table in real code) is required.",
      "Ο δακτύλιος του Kyber είναι X²⁵⁶ + 1, οπότε το twist (ενσωματωμένο στον πίνακα zetas στον πραγματικό κώδικα) είναι απαραίτητο."),
)

INTT = card(
    L("Inverse NTT", "Αντίστροφη NTT"),
    L("Run the same butterflies with inverse roots, then scale every coefficient by n⁻¹.",
      "Τρέχουμε τις ίδιες πεταλούδες με τις αντίστροφες ρίζες και μετά κλιμακώνουμε κάθε συντελεστή με n⁻¹."),
    "INTT(â) = n⁻¹ · NTT_{ω⁻¹}(â)",
    "n = 8, q = 17: n⁻¹ = 15 because 8·15 = 120 = 7·17 + 1",
    L("In ML-KEM the INTT scales by 128⁻¹ mod 3329 = 3303, because the transform has 7 layers (128 pairs), not 8.",
      "Στο ML-KEM η INTT κλιμακώνει με 128⁻¹ mod 3329 = 3303, γιατί ο μετασχηματισμός έχει 7 στρώματα (128 ζεύγη), όχι 8."),
)

BITREV = card(
    L("Bit-reversal order", "Σειρά αντεστραμμένων bits"),
    L("The iterative NTT reads its input in bit-reversed index order.",
      "Η επαναληπτική NTT διαβάζει την είσοδο με σειρά δεικτών αντεστραμμένων bits."),
    "i = (b₂b₁b₀)₂  →  rev(i) = (b₀b₁b₂)₂",
    "1 = 001 → 100 = 4;  3 = 011 → 110 = 6",
    L("FIPS 203 indexes its zeta table as ζ^BitRev₇(k) for exactly this reason.",
      "Το FIPS 203 δεικτοδοτεί τον πίνακα zeta ως ζ^BitRev₇(k) ακριβώς γι' αυτόν τον λόγο."),
)

KEYGEN = card(
    L("Key generation: t̂ = Â·ŝ + ê", "Δημιουργία κλειδιών: t̂ = Â·ŝ + ê"),
    L("The public key is a matrix times the small secret, plus small error, all in the NTT domain.",
      "Το δημόσιο κλειδί είναι ένας πίνακας επί το μικρό μυστικό, συν μικρό σφάλμα, όλα στο πεδίο NTT."),
    "t̂[i] = Σⱼ Â[i][j] ⊙ ŝ[j] + ê[i]",
    "one coefficient: 11·1 + 6·8 + 1 = 60 = 3·17 + 9 → 9",
    L("This is the MLWE problem: given Â and t̂, recovering the small ŝ is believed hard, even for quantum computers.",
      "Αυτό είναι το πρόβλημα MLWE: με γνωστά τα Â και t̂, η ανάκτηση του μικρού ŝ θεωρείται δύσκολη, ακόμη και για κβαντικούς υπολογιστές."),
)

ENCRYPT = card(
    L("Encryption: u and v", "Κρυπτογράφηση: u και v"),
    L("Fresh small r hides the message: u uses the transpose Âᵀ, v uses the public t̂ and carries the message bits.",
      "Ένα φρέσκο μικρό r κρύβει το μήνυμα: το u χρησιμοποιεί τον ανάστροφο Âᵀ, το v χρησιμοποιεί το δημόσιο t̂ και μεταφέρει τα bits."),
    "u = INTT(Âᵀ·r̂) + e₁,   v = INTT(t̂ᵀ·r̂) + e₂ + ⌊q/2⌋·m",
    "bit 1 → ⌊17/2⌋ = 8,  bit 0 → 0",
    L("The transpose makes sᵀ·u and v contain the same large term sᵀAᵀr, so it cancels in decryption.",
      "Ο ανάστροφος κάνει τα sᵀ·u και v να περιέχουν τον ίδιο μεγάλο όρο sᵀAᵀr, ώστε να αλληλοαναιρείται στην αποκρυπτογράφηση."),
)

DECRYPT = card(
    L("Decryption and the noise budget", "Αποκρυπτογράφηση και περιθώριο θορύβου"),
    L("Subtract sᵀ·u from v; what is left is the message plus small noise, rounded to the nearest of 0 or q/2.",
      "Αφαιρούμε το sᵀ·u από το v· μένει το μήνυμα συν μικρό θόρυβο, που στρογγυλεύεται στο πλησιέστερο από 0 ή q/2."),
    "w = v − INTT(ŝᵀ·NTT(u)) ≈ ⌊q/2⌋·m + noise;   correct while |noise| < q/4",
    "w = 10, q = 17: distance to 8 is 2, distance to 0 is 7 → bit 1",
    L("Kyber's parameters are chosen so the noise stays under q/4 except with negligible probability.",
      "Οι παράμετροι του Kyber επιλέγονται ώστε ο θόρυβος να μένει κάτω από q/4, εκτός με αμελητέα πιθανότητα."),
)

HASHES = card(
    L("The five hash roles in FIPS 203", "Οι πέντε ρόλοι hash στο FIPS 203"),
    L("Each job has its own SHA-3 function; swapping them gives a different (wrong) scheme.",
      "Κάθε δουλειά έχει τη δική της συνάρτηση SHA-3· αν τις μπερδέψεις προκύπτει άλλο (λάθος) σχήμα."),
    "G = SHA3-512,  H = SHA3-256,  J = SHAKE256,  XOF = SHAKE128 (matrix A),  PRF = SHAKE256 (noise)",
    "(ρ, σ) = G(d ‖ k);   A[i][j] ← SHAKE128(ρ ‖ j ‖ i);   noise ← SHAKE256(σ ‖ N)",
    L("SHAKE128 expands the public matrix, SHAKE256 makes secret noise. A common mistake is to swap them.",
      "Το SHAKE128 επεκτείνει τον δημόσιο πίνακα, το SHAKE256 φτιάχνει μυστικό θόρυβο. Συνηθισμένο λάθος είναι να μπερδεύονται."),
)

FO = card(
    L("From PKE to KEM: the FO transform", "Από PKE σε KEM: ο μετασχηματισμός FO"),
    L("Derive the key and the encryption coins from the message, then on decapsulation re-encrypt and compare.",
      "Παράγουμε το κλειδί και τα νομίσματα κρυπτογράφησης από το μήνυμα· στην αποσυσκευασία ξανακρυπτογραφούμε και συγκρίνουμε."),
    "(K, r) = G(m ‖ H(ek));  c = Encrypt(ek, m; r);  Decaps: c′ = c ? K′ : J(z ‖ c)",
    "tampered c → c′ ≠ c → return J(z ‖ c), a key the attacker cannot predict",
    L("The raw lattice encryption is only CPA-secure. Re-encryption plus implicit rejection makes ML-KEM IND-CCA2 secure.",
      "Η σκέτη κρυπτογράφηση πλέγματος είναι μόνο CPA-ασφαλής. Η επανακρυπτογράφηση μαζί με την implicit rejection κάνει το ML-KEM IND-CCA2 ασφαλές."),
)

COMPRESS = card(
    L("Compression", "Συμπίεση"),
    L("Keep only the top d bits of each coefficient: a lossy rounding that shrinks the ciphertext.",
      "Κρατάμε μόνο τα d ανώτερα bits κάθε συντελεστή: μια στρογγύλευση με απώλεια που μικραίνει το κρυπτογράφημα."),
    "Compress_d(x) = ⌈(2ᵈ/q)·x⌋ mod 2ᵈ,   Decompress_d(y) = ⌈(q/2ᵈ)·y⌋",
    "q = 3329, d = 1: x = 1665 → ⌈1665·2/3329⌋ = 1;  Decompress_1(1) = 1665",
    L("ML-KEM-512/768 use dᵤ = 10, dᵥ = 4; 1024 uses 11 and 5. The rounding error is part of the noise budget.",
      "Τα ML-KEM-512/768 χρησιμοποιούν dᵤ = 10, dᵥ = 4· το 1024 χρησιμοποιεί 11 και 5. Το σφάλμα στρογγύλευσης μπαίνει στο περιθώριο θορύβου."),
)

SIZES = card(
    L("Parameter sets and sizes", "Σύνολα παραμέτρων και μεγέθη"),
    L("Only the module rank k (and η₁, dᵤ, dᵥ) changes between the three sets; n = 256 and q = 3329 are fixed.",
      "Μόνο η τάξη k (και τα η₁, dᵤ, dᵥ) αλλάζει μεταξύ των τριών συνόλων· τα n = 256 και q = 3329 είναι σταθερά."),
    "ek = 384k + 32,  dk = 768k + 96,  ct = 32(k·dᵤ + dᵥ)  bytes",
    "512: 800 / 1632 / 768    768: 1184 / 2400 / 1088    1024: 1568 / 3168 / 1568",
    L("The shared secret is always 32 bytes.", "Το κοινό μυστικό είναι πάντα 32 bytes."),
)

SECURITY = card(
    L("Why Kyber resists Shor", "Γιατί ο Kyber αντέχει τον Shor"),
    L("Shor's algorithm finds hidden periods (factoring, discrete log). MLWE is not a period-finding problem.",
      "Ο αλγόριθμος του Shor βρίσκει κρυμμένες περιόδους (παραγοντοποίηση, διακριτός λογάριθμος). Το MLWE δεν είναι πρόβλημα εύρεσης περιόδου."),
    "RSA: f(x) = aˣ mod N is periodic → QFT finds the period.   MLWE: t = A·s + e → no period to find",
    "best known attacks on MLWE are lattice reduction, classical or quantum",
    L("That is why NIST standardised ML-KEM as FIPS 203 for post-quantum key exchange.",
      "Γι' αυτό το NIST τυποποίησε το ML-KEM ως FIPS 203 για ανταλλαγή κλειδιών μετά την κβαντική εποχή."),
)

NTT_REAL = card(
    L("Kyber's incomplete NTT", "Η ελλιπής NTT του Kyber"),
    L("3329 − 1 = 2⁸·13, so there is a primitive 256th root (ζ = 17) but no 512th root: X²⁵⁶ + 1 only splits into 128 quadratics.",
      "3329 − 1 = 2⁸·13, άρα υπάρχει πρωταρχική 256η ρίζα (ζ = 17) αλλά όχι 512η: το X²⁵⁶ + 1 σπάει μόνο σε 128 τετραγωνικά."),
    "7 layers → 128 pairs (a₀ + a₁X) mod (X² − γ);  multiply pairs with basemul",
    "basemul: r₀ = a₀b₀ + γ·a₁b₁,  r₁ = a₀b₁ + a₁b₀",
    L("The toy (q = 17) has a 16th root, so its NTT is complete; real Kyber's is not. This is the detail most tutorials miss.",
      "Το toy (q = 17) έχει 16η ρίζα, άρα η NTT του είναι πλήρης· του πραγματικού Kyber όχι. Αυτή είναι η λεπτομέρεια που ξεχνούν τα περισσότερα tutorials."),
)

REDUCE = card(
    L("Fast reduction without division", "Γρήγορη αναγωγή χωρίς διαίρεση"),
    L("Optimised implementations replace % q with a multiply and a shift (Barrett) or work in Montgomery form.",
      "Οι βελτιστοποιημένες υλοποιήσεις αντικαθιστούν το % q με πολλαπλασιασμό και ολίσθηση (Barrett) ή δουλεύουν σε μορφή Montgomery."),
    "Barrett: t = ⌊(v·a + 2²⁵) / 2²⁶⌋, v = ⌊(2²⁶ + q/2)/q⌋ = 20159;   Montgomery: a·2⁻¹⁶ mod q",
    "QINV = q⁻¹ mod 2¹⁶ = −3327 (as int16)",
    L("Division is slow and its timing can depend on the data; these tricks are fast and constant-time. The platform's reference C uses plain % q for clarity.",
      "Η διαίρεση είναι αργή και ο χρόνος της μπορεί να εξαρτάται από τα δεδομένα· αυτά τα κόλπα είναι γρήγορα και σταθερού χρόνου. Η C αναφορά της πλατφόρμας χρησιμοποιεί απλό % q για σαφήνεια."),
)
