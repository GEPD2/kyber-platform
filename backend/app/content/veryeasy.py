"""Level 1: Very Easy. Hand arithmetic on the toy numbers (q = 17)."""
from app.content import cards as C
from app.content.schema import L, duo

S_RING = L("Ring arithmetic", "Αριθμητική δακτυλίου")
S_CBD = L("Noise sampling", "Δειγματοληψία θορύβου")
S_NTT = L("NTT", "NTT")
S_DEC = L("Decryption", "Αποκρυπτογράφηση")

QUESTIONS = [
duo("ve-mod", S_RING,
    L("Compute <b>25 mod 17</b>.", "Υπολόγισε <b>25 mod 17</b>."),
    "25 mod 17 =", ["8"], C.MOD,
    [L("mod is the remainder after dividing by 17.", "Το mod είναι το υπόλοιπο της διαίρεσης με το 17."),
     L("25 = 1·17 + ?", "25 = 1·17 + ;")],
    L("25 − 17 = 8. Every Kyber coefficient is kept in {0, …, q−1} this way.",
      "25 − 17 = 8. Κάθε συντελεστής του Kyber κρατιέται έτσι στο {0, …, q−1}.")),

duo("ve-neg", S_RING,
    L("Compute <b>−2 mod 17</b>.", "Υπολόγισε <b>−2 mod 17</b>."),
    "−2 mod 17 =", ["15"], C.NEG,
    [L("The result must be in {0, …, 16}.", "Το αποτέλεσμα πρέπει να είναι στο {0, …, 16}."),
     L("Add q once: −2 + 17.", "Πρόσθεσε το q μία φορά: −2 + 17.")],
    L("−2 + 17 = 15. CBD noise of −2 is stored as 15.", "−2 + 17 = 15. Θόρυβος CBD ίσος με −2 αποθηκεύεται ως 15.")),

duo("ve-negacyclic", S_RING,
    L("In Z₁₇[X]/(X⁸ + 1), reduce <b>2·X⁹</b>. What is the coefficient of X?",
      "Στο Z₁₇[X]/(X⁸ + 1), ανάγαγε το <b>2·X⁹</b>. Ποιος είναι ο συντελεστής του X;"),
    "coeff of X =", ["15"], C.RING,
    [L("X⁸ wraps round to −1.", "Το X⁸ τυλίγεται σε −1."),
     L("2·X⁹ = 2·X⁸·X = −2·X; then take −2 mod 17.", "2·X⁹ = 2·X⁸·X = −2·X· μετά πάρε −2 mod 17.")],
    L("X⁹ = −X, so 2·X⁹ = −2·X and −2 ≡ 15. The minus sign is what 'negacyclic' means.",
      "X⁹ = −X, άρα 2·X⁹ = −2·X και −2 ≡ 15. Το πρόσημο μείον είναι αυτό που σημαίνει «negacyclic».")),

duo("ve-cbd-neg", S_CBD,
    L("Byte <code>0x0C</code> = 00001100. Read LSB first, bits 0–3 are b₀=0, b₁=0, b₂=1, b₃=1. What is the <b>stored</b> coefficient (mod 17)?",
      "Byte <code>0x0C</code> = 00001100. Από το LSB, τα bits 0–3 είναι b₀=0, b₁=0, b₂=1, b₃=1. Ποιος είναι ο <b>αποθηκευμένος</b> συντελεστής (mod 17);"),
    "coeff[0] =", ["15"], C.CBD,
    [L("CBD subtracts the second pair from the first.", "Το CBD αφαιρεί το δεύτερο ζεύγος από το πρώτο."),
     L("(b₀ + b₁) − (b₂ + b₃), then reduce a negative value mod 17.", "(b₀ + b₁) − (b₂ + b₃), και μετά ανάγαγε την αρνητική τιμή mod 17.")],
    L("(0 + 0) − (1 + 1) = −2, stored as 15.", "(0 + 0) − (1 + 1) = −2, αποθηκεύεται ως 15.")),

duo("ve-cbd-pos", S_CBD,
    L("Byte <code>0x03</code> = 00000011. Bits 0–3 are b₀=1, b₁=1, b₂=0, b₃=0. What is coeff[0]?",
      "Byte <code>0x03</code> = 00000011. Τα bits 0–3 είναι b₀=1, b₁=1, b₂=0, b₃=0. Πόσο είναι το coeff[0];"),
    "coeff[0] =", ["2"], C.CBD,
    [L("Same formula as before.", "Ίδιος τύπος με πριν."),
     L("(b₀ + b₁) − (b₂ + b₃).", "(b₀ + b₁) − (b₂ + b₃).")],
    L("(1 + 1) − (0 + 0) = 2, the largest value η = 2 can produce.",
      "(1 + 1) − (0 + 0) = 2, η μεγαλύτερη τιμή που μπορεί να δώσει το η = 2.")),

duo("ve-root", S_NTT,
    L("ω = 9. Compute <b>ROOTS[3] = ω³ mod 17</b>.", "ω = 9. Υπολόγισε <b>ROOTS[3] = ω³ mod 17</b>."),
    "ω³ mod 17 =", ["15"], C.ROOTS,
    [L("Build on ω² = 13.", "Ξεκίνα από το ω² = 13."),
     L("ω³ = 13·9 = 117; reduce mod 17.", "ω³ = 13·9 = 117· ανάγαγε mod 17.")],
    L("117 = 6·17 + 15. The powers of ω are 1, 9, 13, 15, 16, 8, 4, 2.",
      "117 = 6·17 + 15. Οι δυνάμεις του ω είναι 1, 9, 13, 15, 16, 8, 4, 2.")),

duo("ve-bf-u", S_NTT,
    L("Butterfly with <b>u = 3, v = 1, w = 9, q = 17</b>. What is u′?",
      "Πεταλούδα με <b>u = 3, v = 1, w = 9, q = 17</b>. Πόσο είναι το u′;"),
    "u′ =", ["12"], C.BUTTERFLY,
    [L("First compute t from v and w.", "Πρώτα υπολόγισε το t από τα v και w."),
     L("t = v·w mod q, then u′ = (u + t) mod q.", "t = v·w mod q, μετά u′ = (u + t) mod q.")],
    L("t = 9, u′ = 3 + 9 = 12.", "t = 9, u′ = 3 + 9 = 12.")),

duo("ve-bf-v", S_NTT,
    L("Same butterfly: <b>u = 3, v = 1, w = 9, q = 17</b>. What is v′?",
      "Ίδια πεταλούδα: <b>u = 3, v = 1, w = 9, q = 17</b>. Πόσο είναι το v′;"),
    "v′ =", ["11"], C.BUTTERFLY,
    [L("The second output subtracts.", "Η δεύτερη έξοδος αφαιρεί."),
     L("v′ = (u − t) mod q with t = 9.", "v′ = (u − t) mod q με t = 9.")],
    L("3 − 9 = −6 ≡ 11.", "3 − 9 = −6 ≡ 11.")),

duo("ve-pointwise", S_NTT,
    L("In the NTT domain one coefficient of a product is a single multiply: <b>11 · 3 mod 17</b>.",
      "Στο πεδίο NTT ένας συντελεστής του γινομένου είναι ένας πολλαπλασιασμός: <b>11 · 3 mod 17</b>."),
    "11·3 mod 17 =", ["16"], C.NTT,
    [L("Multiply, then reduce.", "Πολλαπλασίασε, μετά ανάγαγε."),
     L("33 = 1·17 + ?", "33 = 1·17 + ;")],
    L("33 − 17 = 16. In the toy every coefficient is independent; in real Kyber they come in pairs (basemul).",
      "33 − 17 = 16. Στο toy κάθε συντελεστής είναι ανεξάρτητος· στον πραγματικό Kyber έρχονται σε ζεύγη (basemul).")),

duo("ve-decode", S_DEC,
    L("Decode <b>w = 3</b> with q = 17: is the bit 0 or 1?", "Αποκωδικοποίησε <b>w = 3</b> με q = 17: το bit είναι 0 ή 1;"),
    "bit =", ["0"], C.DECRYPT,
    [L("Bit 1 sits at 8, bit 0 at 0. Which is closer (going round the circle)?",
       "Το bit 1 βρίσκεται στο 8, το bit 0 στο 0. Ποιο είναι πιο κοντά (κυκλικά);"),
     L("Distance to 0 is min(3, 17 − 3); distance to 8 is min(|3 − 8|, 17 − |3 − 8|).",
       "Απόσταση από 0: min(3, 17 − 3)· από 8: min(|3 − 8|, 17 − |3 − 8|).")],
    L("Distance to 0 is 3, to 8 is 5, so the bit is 0.", "Απόσταση από 0 είναι 3, από 8 είναι 5, άρα το bit είναι 0.")),
]
