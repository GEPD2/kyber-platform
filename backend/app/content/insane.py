"""
Level 6: Insane. Real ML-KEM in C. Every template with ref=True is checked to
appear verbatim (comments and whitespace aside) in the canonical FIPS 203
reference, tests/data/kyber_fips203_update.c, and every distractor is checked
NOT to. The two optimisation questions (Barrett, Montgomery) come from the
pq-crystals implementation and are compiled and tested exhaustively instead.
"""
from app.content import cards as C
from app.content.schema import L, choice, gaps, text

S_NTT = L("NTT in C", "NTT σε C")
S_SAMPLE = L("Sampling", "Δειγματοληψία")
S_PKE = L("K-PKE", "K-PKE")
S_KEM = L("ML-KEM", "ML-KEM")
S_OPT = L("Optimisation", "Βελτιστοποίηση")

QUESTIONS = [
gaps("in-ntt", S_NTT,
     L("Complete the forward NTT (7 layers, plain mod-q arithmetic).", "Συμπλήρωσε την ευθεία NTT (7 στρώματα, απλή αριθμητική mod q)."),
     "c", """
static void poly_ntt(poly f){
    int k=1;
    for(int len=[[0]];len>=2;len>>=1)
        for(int start=0;start<KYBER_N;start+=2*len){
            int z=zetas[[[1]]];
            for(int j=start;j<start+len;j++){
                int t=(int)z*f[j+len]%KYBER_Q;
                f[j+len]=(int16_t)((f[j]-t+[[2]])%KYBER_Q);
                f[j]=(int16_t)((f[j]+t)%KYBER_Q);
            }
        }
}
""",
     [text(["128", "KYBER_N/2"], "ntt_layers",
           [L("The first layer pairs coefficient j with j + n/2.", "Το πρώτο στρώμα ζευγαρώνει τον συντελεστή j με τον j + n/2."),
            L("Half of 256; the loop stops at 2, giving 7 layers.", "Το μισό του 256· ο βρόχος σταματά στο 2, άρα 7 στρώματα.")], width=6),
      choice(["k++", "k", "len", "j"], 0, "roots",
             [L("Each block gets the next zeta from the bit-reversed table.", "Κάθε μπλοκ παίρνει το επόμενο zeta από τον πίνακα σε σειρά bit-reversal."),
              L("Read the current entry, then advance the index.", "Διάβασε την τρέχουσα θέση και μετά προχώρα τον δείκτη.")]),
      choice(["KYBER_Q", "0", "KYBER_Q/2"], 0, "modular",
             [L("In C, % of a negative number is negative.", "Στη C, το % αρνητικού αριθμού είναι αρνητικό."),
              L("Add the modulus before reducing so the value stays non-negative.", "Πρόσθεσε το modulus πριν την αναγωγή ώστε η τιμή να μείνει μη αρνητική.")])],
     C.NTT_REAL,
     L("len runs 128, 64, …, 2 (7 layers) and the zetas are consumed in order. The +KYBER_Q avoids a negative remainder.",
       "Το len παίρνει 128, 64, …, 2 (7 στρώματα) και τα zetas καταναλώνονται με τη σειρά. Το +KYBER_Q αποφεύγει αρνητικό υπόλοιπο."),
     ref=True),

gaps("in-intt", S_NTT,
     L("Complete the inverse NTT.", "Συμπλήρωσε την αντίστροφη NTT."),
     "c", """
static void poly_intt(poly f){
    int k=[[0]];
    for(int len=2;len<=128;len<<=1)
        for(int start=0;start<KYBER_N;start+=2*len){
            int z=zetas[k--];
            for(int j=start;j<start+len;j++){
                int t=f[j];
                f[j]=(int16_t)((t+f[j+len])%KYBER_Q);
                f[j+len]=(int16_t)((int)z*((f[j+len]-t+KYBER_Q)%KYBER_Q)%KYBER_Q);
            }
        }
    for(int i=0;i<KYBER_N;i++) f[i]=(int16_t)((int)f[i]*[[1]]%KYBER_Q);
}
""",
     [text(["127"], "roots",
           [L("The inverse walks the zeta table backwards.", "Η αντίστροφη διατρέχει τον πίνακα zeta ανάποδα."),
            L("Start at the last entry of a 128-entry table.", "Ξεκίνα από την τελευταία θέση ενός πίνακα 128 θέσεων.")], width=5),
      choice(["N_INV", "KYBER_N", "1441", "3316"], 0, "n_inv",
             [L("Undo the factor the 7 layers introduced.", "Αναίρεσε τον παράγοντα που εισήγαγαν τα 7 στρώματα."),
              L("128⁻¹ mod q in the plain (non-Montgomery) domain.", "128⁻¹ mod q στο απλό (όχι Montgomery) πεδίο.")])],
     C.INTT,
     L("k starts at 127 and counts down; the final scale is N_INV = 3303 = 128⁻¹. 1441 is the Montgomery-form constant of pq-crystals and 3316 is 256⁻¹: both wrong here.",
       "Το k ξεκινά από 127 και μετρά προς τα κάτω· η τελική κλιμάκωση είναι N_INV = 3303 = 128⁻¹. Το 1441 είναι η σταθερά σε μορφή Montgomery του pq-crystals και το 3316 είναι 256⁻¹: και τα δύο λάθος εδώ."),
     ref=True),

gaps("in-basemul", S_NTT,
     L("Complete basemul: products of degree-1 pairs mod (X² − γ).", "Συμπλήρωσε το basemul: γινόμενα ζευγών βαθμού 1 mod (X² − γ)."),
     "c", """
static void poly_basemul(poly r,const poly a,const poly b){
    for(int g=0;g<64;g++){
        long gp=zetas[[[0]]], gn=[[1]]; int i=4*g;
        r[i]  =(int16_t)(((long)a[i]*b[i]+gp*a[i+1]%KYBER_Q*b[i+1])%KYBER_Q);
        r[i+1]=(int16_t)(((long)a[i]*b[i+1]+(long)a[i+1]*b[i])%KYBER_Q);
        i=4*g+2;
        r[i]  =(int16_t)(((long)a[i]*b[i]+gn*a[i+1]%KYBER_Q*b[i+1])%KYBER_Q);
        r[i+1]=(int16_t)(((long)a[i]*b[i+1]+(long)a[i+1]*b[i])%KYBER_Q);
    }
}
""",
     [choice(["64+g", "g", "128+g", "2*g"], 0, "basemul",
             [L("The γ values are the roots used by the last NTT layer.", "Οι τιμές γ είναι οι ρίζες του τελευταίου στρώματος NTT."),
              L("That layer uses the upper half of the 128-entry table.", "Εκείνο το στρώμα χρησιμοποιεί το πάνω μισό του πίνακα των 128.")]),
      choice(["KYBER_Q-gp", "gp", "-1"], 0, "basemul",
             [L("Each quadratic factor comes paired with its negative.", "Κάθε τετραγωνικός παράγοντας έρχεται σε ζεύγος με τον αρνητικό του."),
              L("X² − γ and X² + γ; −γ mod q.", "X² − γ και X² + γ· −γ mod q.")])],
     C.NTT_REAL,
     L("Pairs 4g and 4g+2 use +ζ and −ζ with ζ = zetas[64+g]. The casts to long stop γ·a·b (up to q³) overflowing.",
       "Τα ζεύγη 4g και 4g+2 χρησιμοποιούν +ζ και −ζ με ζ = zetas[64+g]. Τα casts σε long εμποδίζουν την υπερχείλιση του γ·a·b (έως q³)."),
     ref=True),

gaps("in-gen-a", S_SAMPLE,
     L("Complete the generation of one entry A[R][C].", "Συμπλήρωσε τη δημιουργία ενός στοιχείου A[R][C]."),
     "c", """
static void gen_a_entry(poly out,const uint8_t rho[SEED_BYTES],int R,int C){
    uint8_t seed[SEED_BYTES+2];
    memcpy(seed,rho,SEED_BYTES); seed[SEED_BYTES]=(uint8_t)[[0]]; seed[SEED_BYTES+1]=(uint8_t)[[1]];
    Keccak c; xof_init(&c,[[2]]); xof_absorb(&c,seed,SEED_BYTES+2); xof_finalize(&c,0x1F);
    int count=0,bp=0,bl=0; uint8_t buf[168*4];
    while(count<KYBER_N){
        if(bp+3>bl){ xof_squeeze(&c,buf,sizeof(buf)); bl=sizeof(buf); bp=0; }
        uint8_t b0=buf[bp],b1=buf[bp+1],b2=buf[bp+2]; bp+=3;
        int d1=b0|((b1&0x0F)<<8), d2=(b1>>4)|((int)b2<<4);
        if(d1<[[3]]&&count<KYBER_N) out[count++]=(int16_t)d1;
        if(d2<KYBER_Q&&count<KYBER_N) out[count++]=(int16_t)d2;
    }
}
""",
     [choice(["C", "R"], 0, "matrix",
             [L("FIPS 203 hashes ρ ‖ j ‖ i for A[i][j].", "Το FIPS 203 κάνει hash το ρ ‖ j ‖ i για το A[i][j]."),
              L("The first extra byte is the column.", "Το πρώτο επιπλέον byte είναι η στήλη.")]),
      choice(["R", "C"], 0, "matrix",
             [L("The last byte is the other index.", "Το τελευταίο byte είναι ο άλλος δείκτης."),
              L("ρ ‖ j ‖ i: the row comes last.", "ρ ‖ j ‖ i: η γραμμή μπαίνει τελευταία.")]),
      choice(["168", "136", "72"], 0, "hash_role",
             [L("This is SHAKE128; the rate is 1600 − 2·128 bits.", "Αυτό είναι SHAKE128· ο ρυθμός είναι 1600 − 2·128 bits."),
              L("1344 bits in bytes.", "1344 bits σε bytes.")]),
      choice(["KYBER_Q", "4096", "KYBER_Q+1"], 0, "sampling",
             [L("Keep only values that are already valid coefficients.", "Κράτα μόνο τιμές που είναι ήδη έγκυροι συντελεστές."),
              L("Reject 12-bit candidates outside Z_q.", "Απόρριψε υποψήφιους 12 bits εκτός Z_q.")])],
     C.HASHES,
     L("SHAKE128 (rate 168) on ρ ‖ C ‖ R, rejecting candidates ≥ q. 136 is the SHAKE256 rate and 72 the SHA3-512 rate.",
       "SHAKE128 (ρυθμός 168) στο ρ ‖ C ‖ R, με απόρριψη υποψηφίων ≥ q. Το 136 είναι ο ρυθμός του SHAKE256 και το 72 του SHA3-512."),
     ref=True),

gaps("in-cbd", S_SAMPLE,
     L("Complete CBD for any η.", "Συμπλήρωσε το CBD για οποιοδήποτε η."),
     "c", """
static void cbd(poly f,const uint8_t*buf,int eta){
    for(int i=0;i<KYBER_N;i++){
        int base=[[0]]*i,a=0,b=0;
        for(int j=0;j<eta;j++) a+=getbit(buf,base+j);
        for(int j=0;j<eta;j++) b+=getbit(buf,base+[[1]]+j);
        int v=a-b; f[i]=(int16_t)(((v%KYBER_Q)+KYBER_Q)%KYBER_Q);
    }
}
""",
     [text(["2*eta", "eta*2"], "cbd",
           [L("How many random bits does one coefficient consume?", "Πόσα τυχαία bits καταναλώνει ένας συντελεστής;"),
            L("η bits for a, η bits for b.", "η bits για το a, η bits για το b.")], width=7),
      choice(["eta", "1", "2*eta"], 0, "cbd",
             [L("b reads the second half of this coefficient's bits.", "Το b διαβάζει το δεύτερο μισό των bits του συντελεστή."),
              L("Skip past the η bits used by a.", "Προσπέρασε τα η bits που χρησιμοποίησε το a.")])],
     C.CBD,
     L("Each coefficient uses 2η bits: popcount of the first η minus popcount of the next η.",
       "Κάθε συντελεστής χρησιμοποιεί 2η bits: πλήθος άσσων στα πρώτα η μείον στα επόμενα η."),
     ref=True),

gaps("in-prf", S_SAMPLE,
     L("Complete the noise PRF call.", "Συμπλήρωσε την κλήση της PRF θορύβου."),
     "c", """
static void sample_poly(poly f,const uint8_t seed[SEED_BYTES],uint8_t nonce,int eta){
    uint8_t in[SEED_BYTES+1]; memcpy(in,seed,SEED_BYTES); in[SEED_BYTES]=nonce;
    uint8_t buf[64*3]; [[0]](in,SEED_BYTES+1,buf,(size_t)[[1]]*eta); cbd(f,buf,eta);
}
""",
     [choice(["shake256", "shake128", "sha3_512"], 0, "hash_role",
             [L("This output is secret noise.", "Αυτή η έξοδος είναι μυστικός θόρυβος."),
              L("PRF = the stronger SHAKE.", "PRF = το ισχυρότερο SHAKE.")]),
      text(["64"], "cbd",
           [L("256 coefficients × 2η bits, in bytes.", "256 συντελεστές × 2η bits, σε bytes."),
            L("512·η bits ÷ 8.", "512·η bits ÷ 8.")], width=4)],
     C.HASHES,
     L("PRF = SHAKE256(σ ‖ N) producing 64·η bytes: 192 for η = 3, 128 for η = 2.",
       "PRF = SHAKE256(σ ‖ N) που παράγει 64·η bytes: 192 για η = 3, 128 για η = 2."),
     ref=True),

gaps("in-compress", S_PKE,
     L("Complete Compress_d and Decompress_d with integer rounding.", "Συμπλήρωσε τα Compress_d και Decompress_d με ακέραια στρογγύλευση."),
     "c", """
static inline int compress_c(int x,int d){ return (int)(((((long)x)<<d)+[[0]])/KYBER_Q)&((1<<d)-1); }
static inline int decompress_c(int y,int d){ return (int)(((long)KYBER_Q*y+[[1]])>>d); }
""",
     [choice(["KYBER_Q/2", "KYBER_Q", "0"], 0, "compress",
             [L("Round to nearest instead of truncating.", "Στρογγύλευσε στο πλησιέστερο αντί να αποκόψεις."),
              L("Add half of the divisor.", "Πρόσθεσε το μισό του διαιρέτη.")]),
      choice(["(1<<(d-1))", "(1<<d)", "KYBER_Q/2"], 0, "compress",
             [L("Here the divisor is 2ᵈ (the >> d).", "Εδώ ο διαιρέτης είναι 2ᵈ (το >> d)."),
              L("Half of 2ᵈ.", "Το μισό του 2ᵈ.")])],
     C.COMPRESS,
     L("Both directions round by adding half the divisor: q/2 before /q, 2ᵈ⁻¹ before >>d.",
       "Και οι δύο κατευθύνσεις στρογγυλεύουν προσθέτοντας το μισό του διαιρέτη: q/2 πριν το /q, 2ᵈ⁻¹ πριν το >>d."),
     ref=True),

gaps("in-keygen", S_PKE,
     L("Complete the start of K-PKE.KeyGen.", "Συμπλήρωσε την αρχή του K-PKE.KeyGen."),
     "c", """
static void kpke_keygen(const uint8_t d[SEED_BYTES],uint8_t ek[PKE_PK_BYTES],uint8_t dk[PKE_SK_BYTES]){
    uint8_t de[SEED_BYTES+1]; memcpy(de,d,SEED_BYTES); de[SEED_BYTES]=(uint8_t)[[0]];
    uint8_t rs[64]; [[1]](de,SEED_BYTES+1,rs);
    uint8_t *rho=rs,*sigma=rs+32;
    poly s[KYBER_K],e[KYBER_K],t[KYBER_K];
    for(int i=0;i<KYBER_K;i++){
        sample_poly(s[i],sigma,(uint8_t)i,KYBER_ETA1);
        sample_poly(e[i],sigma,(uint8_t)([[2]]),KYBER_ETA1);
        poly_ntt(s[i]); poly_ntt(e[i]);
    }
    /* t = A*s + e and the byte encoding follow */
""",
     [text(["KYBER_K"], "hash_role",
           [L("Domain separation by parameter set.", "Διαχωρισμός πεδίου ανά σύνολο παραμέτρων."),
            L("G(d ‖ k).", "G(d ‖ k).")], width=8),
      choice(["sha3_512", "sha3_256", "shake256"], 0, "hash_role",
             [L("This is G; it yields ρ and σ together.", "Αυτό είναι το G· δίνει μαζί ρ και σ."),
              L("64 bytes, fixed length.", "64 bytes, σταθερό μήκος.")]),
      choice(["KYBER_K+i", "i", "i+1"], 0, "noise",
             [L("s used nonces 0 … k−1.", "Το s χρησιμοποίησε nonces 0 … k−1."),
              L("e continues from k.", "Το e συνεχίζει από το k.")])],
     C.KEYGEN,
     L("(ρ, σ) = G(d ‖ k), s gets nonces 0…k−1 and e gets k…2k−1, both sampled with η₁.",
       "(ρ, σ) = G(d ‖ k), το s παίρνει nonces 0…k−1 και το e k…2k−1, και τα δύο με η₁."),
     ref=True),

gaps("in-enc-u", S_PKE,
     L("Complete the u part of K-PKE.Encrypt.", "Συμπλήρωσε το κομμάτι u του K-PKE.Encrypt."),
     "c", """
    for(int i=0;i<KYBER_K;i++) sample_poly(r[i],coins,N++,[[0]]);
    for(int i=0;i<KYBER_K;i++) sample_poly(e1[i],coins,N++,KYBER_ETA2);
    sample_poly(e2,coins,N++,KYBER_ETA2);
    for(int i=0;i<KYBER_K;i++){ memcpy(rhat[i],r[i],sizeof(poly)); poly_ntt(rhat[i]); }
    poly u[KYBER_K];
    for(int i=0;i<KYBER_K;i++){
        poly acc; memset(acc,0,sizeof(acc)); poly a,tmp;
        for(int j=0;j<KYBER_K;j++){ gen_a_entry(a,rho,[[1]]); poly_basemul(tmp,a,rhat[j]); poly_add(acc,acc,tmp); }
        poly_intt(acc); poly_add(u[i],acc,e1[i]);
    }
""",
     [choice(["KYBER_ETA1", "KYBER_ETA2"], 0, "noise",
             [L("r plays the role that s plays in key generation.", "Το r παίζει τον ρόλο που παίζει το s στη δημιουργία κλειδιών."),
              L("It uses the same noise width as s.", "Χρησιμοποιεί το ίδιο πλάτος θορύβου με το s.")]),
      choice(["j,i", "i,j"], 0, "transpose",
             [L("u uses Aᵀ.", "Το u χρησιμοποιεί τον Aᵀ."),
              L("Transposing swaps the roles of the row and column index.", "Η αναστροφή ανταλλάσσει τους ρόλους των δεικτών γραμμής και στήλης.")])],
     C.ENCRYPT,
     L("r uses η₁ (3 for ML-KEM-512), e₁ and e₂ use η₂ = 2, and the matrix is read transposed.",
       "Το r χρησιμοποιεί η₁ (3 για ML-KEM-512), τα e₁ και e₂ χρησιμοποιούν η₂ = 2, και ο πίνακας διαβάζεται ανάστροφα."),
     ref=True),

gaps("in-enc-v", S_PKE,
     L("Complete v and the compression of the ciphertext.", "Συμπλήρωσε το v και τη συμπίεση του κρυπτογραφήματος."),
     "c", """
    poly v,acc; memset(acc,0,sizeof(acc)); poly tmp;
    for(int j=0;j<KYBER_K;j++){ poly_basemul(tmp,t[j],rhat[j]); poly_add(acc,acc,tmp); }
    poly_intt(acc); poly mu; poly_decompress(mu,m,[[0]]);
    poly_add(v,acc,e2); poly_add(v,v,mu);
    for(int i=0;i<KYBER_K;i++) poly_compress(c+i*32*KYBER_DU,u[i],[[1]]);
    poly_compress(c+CT_C1_BYTES,v,[[2]]);
""",
     [text(["1"], "encode",
           [L("Each message bit becomes 0 or about q/2.", "Κάθε bit μηνύματος γίνεται 0 ή περίπου q/2."),
            L("Decompress with the smallest possible d.", "Decompress με το μικρότερο δυνατό d.")], width=3),
      choice(["KYBER_DU", "KYBER_DV", "12"], 0, "compress",
             [L("u is the larger part of the ciphertext.", "Το u είναι το μεγαλύτερο κομμάτι του κρυπτογραφήματος."),
              L("10 bits for 512 and 768.", "10 bits για 512 και 768.")]),
      choice(["KYBER_DV", "KYBER_DU", "12"], 0, "compress",
             [L("v can be compressed harder.", "Το v μπορεί να συμπιεστεί περισσότερο."),
              L("4 bits for 512 and 768.", "4 bits για 512 και 768.")])],
     C.COMPRESS,
     L("Decompress₁ maps bit 1 to ⌈q/2⌋ = 1665. u is kept at dᵤ bits and v at dᵥ bits; 12 would mean no compression.",
       "Το Decompress₁ στέλνει το bit 1 στο ⌈q/2⌋ = 1665. Το u κρατιέται σε dᵤ bits και το v σε dᵥ bits· το 12 θα σήμαινε καμία συμπίεση."),
     ref=True),

gaps("in-decrypt", S_PKE,
     L("Complete K-PKE.Decrypt.", "Συμπλήρωσε το K-PKE.Decrypt."),
     "c", """
static void kpke_decrypt(const uint8_t dk[PKE_SK_BYTES],const uint8_t c[CT_BYTES],uint8_t m[32]){
    poly u[KYBER_K],v;
    for(int i=0;i<KYBER_K;i++) poly_decompress(u[i],c+i*32*KYBER_DU,KYBER_DU);
    poly_decompress(v,c+CT_C1_BYTES,KYBER_DV);
    poly s[KYBER_K]; for(int i=0;i<KYBER_K;i++) byte_decode(s[i],dk+i*POLY_BYTES,[[0]]);
    poly acc; memset(acc,0,sizeof(acc)); poly tmp;
    for(int j=0;j<KYBER_K;j++){ [[1]]; poly_basemul(tmp,s[j],u[j]); poly_add(acc,acc,tmp); }
    poly_intt(acc); poly w; poly_sub(w,[[2]],acc);
    poly_compress(m,w,1);
}
""",
     [text(["12"], "serialise",
           [L("The secret key is stored uncompressed.", "Το μυστικό κλειδί αποθηκεύεται χωρίς συμπίεση."),
            L("Enough bits for any value below 3329.", "Αρκετά bits για κάθε τιμή κάτω από 3329.")], width=4),
      choice(["poly_ntt(u[j])", "poly_intt(u[j])", "poly_ntt(s[j])"], 0, "ntt_layers",
             [L("s is stored in the NTT domain, u is not.", "Το s αποθηκεύεται στο πεδίο NTT, το u όχι."),
              L("Bring u into the same domain as s.", "Φέρε το u στο ίδιο πεδίο με το s.")]),
      choice(["v", "acc", "u[0]"], 0, "decode",
             [L("Which part carries the message?", "Ποιο κομμάτι μεταφέρει το μήνυμα;"),
              L("w = v − sᵀ·u.", "w = v − sᵀ·u.")])],
     C.DECRYPT,
     L("ŝ is decoded with 12 bits, u is moved to the NTT domain, and w = v − INTT(ŝᵀ·û) is rounded with Compress₁.",
       "Το ŝ αποκωδικοποιείται με 12 bits, το u μεταφέρεται στο πεδίο NTT, και το w = v − INTT(ŝᵀ·û) στρογγυλεύεται με Compress₁."),
     ref=True),

gaps("in-kem-keygen", S_KEM,
     L("Complete ML-KEM.KeyGen: dk = dk_PKE ‖ ek ‖ H(ek) ‖ z.", "Συμπλήρωσε το ML-KEM.KeyGen: dk = dk_PKE ‖ ek ‖ H(ek) ‖ z."),
     "c", """
static void mlkem_keygen(const uint8_t d[SEED_BYTES],const uint8_t z[SEED_BYTES],uint8_t ek[PKE_PK_BYTES],uint8_t dk[DK_BYTES]){
    uint8_t dkpke[PKE_SK_BYTES];
    kpke_keygen(d,ek,dkpke);
    memcpy(dk,dkpke,PKE_SK_BYTES);
    memcpy(dk+PKE_SK_BYTES,ek,PKE_PK_BYTES);
    [[0]](ek,PKE_PK_BYTES,dk+PKE_SK_BYTES+PKE_PK_BYTES);
    memcpy(dk+PKE_SK_BYTES+PKE_PK_BYTES+32,[[1]],SEED_BYTES);
}
""",
     [choice(["sha3_256", "sha3_512", "shake128"], 0, "hash_role",
             [L("This is H.", "Αυτό είναι το H."),
              L("32-byte fixed output.", "Έξοδος 32 bytes σταθερού μήκους.")]),
      choice(["z", "d", "ek"], 0, "implicit_reject",
             [L("The last 32 bytes are the implicit-rejection secret.", "Τα τελευταία 32 bytes είναι το μυστικό της implicit rejection."),
              L("Not the key-generation seed: that must not be stored.", "Όχι ο σπόρος της δημιουργίας κλειδιών: αυτός δεν πρέπει να αποθηκεύεται.")])],
     C.FO,
     L("H(ek) = SHA3-256 is cached in dk, and z is appended for J(z ‖ c).",
       "Το H(ek) = SHA3-256 αποθηκεύεται στο dk, και το z προστίθεται για το J(z ‖ c)."),
     ref=True),

gaps("in-encaps", S_KEM,
     L("Complete ML-KEM.Encaps.", "Συμπλήρωσε το ML-KEM.Encaps."),
     "c", """
static void mlkem_encaps(const uint8_t ek[PKE_PK_BYTES],const uint8_t m[32],uint8_t K[SS_BYTES],uint8_t c[CT_BYTES]){
    uint8_t g_in[64]; memcpy(g_in,m,32); sha3_256(ek,PKE_PK_BYTES,g_in+32);
    uint8_t Kr[64]; [[0]](g_in,64,Kr);
    memcpy(K,Kr,32);
    kpke_encrypt(ek,m,[[1]],c);
}
""",
     [choice(["sha3_512", "sha3_256", "shake256"], 0, "hash_role",
             [L("This is G: it must give both K and r.", "Αυτό είναι το G: πρέπει να δώσει και K και r."),
              L("64 bytes of output.", "64 bytes εξόδου.")]),
      choice(["Kr+32", "Kr", "m"], 0, "fo_transform",
             [L("K is the first half; the coins are the rest.", "Το K είναι το πρώτο μισό· τα νομίσματα είναι το υπόλοιπο."),
              L("Second 32 bytes of G's output.", "Τα δεύτερα 32 bytes της εξόδου του G.")])],
     C.FO,
     L("(K, r) = G(m ‖ H(ek)); c = Encrypt(ek, m; r). There is no extra KDF over the ciphertext, unlike round-3 Kyber.",
       "(K, r) = G(m ‖ H(ek))· c = Encrypt(ek, m; r). Δεν υπάρχει επιπλέον KDF πάνω στο κρυπτογράφημα, σε αντίθεση με το Kyber round-3."),
     ref=True),

gaps("in-decaps", S_KEM,
     L("Complete ML-KEM.Decaps.", "Συμπλήρωσε το ML-KEM.Decaps."),
     "c", """
    uint8_t mp[32]; kpke_decrypt(dkpke,c,mp);
    uint8_t g_in[64]; memcpy(g_in,mp,32); memcpy(g_in+32,h,32);
    uint8_t Kr[64]; sha3_512(g_in,64,Kr);
    uint8_t cprime[CT_BYTES]; kpke_encrypt([[0]],mp,Kr+32,cprime);
    uint8_t Kbar[32]; { uint8_t zc[SEED_BYTES+CT_BYTES];
        memcpy(zc,z,SEED_BYTES); memcpy(zc+SEED_BYTES,c,CT_BYTES);
        [[1]](zc,SEED_BYTES+CT_BYTES,Kbar,32); }
    int diff=0; for(int i=0;i<CT_BYTES;i++) diff|=c[i]^cprime[i];
    if(diff==0) memcpy(K,[[2]],32); else memcpy(K,[[3]],32);
""",
     [choice(["ek", "dkpke", "h"], 0, "fo_transform",
             [L("Re-encryption uses the public key stored inside dk.", "Η επανακρυπτογράφηση χρησιμοποιεί το δημόσιο κλειδί που είναι μέσα στο dk."),
              L("Encrypt always takes the encapsulation key.", "Το Encrypt παίρνει πάντα το κλειδί ενθυλάκωσης.")]),
      choice(["shake256", "sha3_256", "shake128"], 0, "hash_role",
             [L("This is J.", "Αυτό είναι το J."),
              L("An XOF asked for 32 bytes.", "Ένα XOF που ζητά 32 bytes.")]),
      choice(["Kr", "Kbar"], 0, "implicit_reject",
             [L("The ciphertexts match: the sender was honest.", "Τα κρυπτογραφήματα ταιριάζουν: ο αποστολέας ήταν τίμιος."),
              L("Use the re-derived key.", "Χρησιμοποίησε το κλειδί που ξαναπαράχθηκε.")]),
      choice(["Kbar", "Kr"], 0, "implicit_reject",
             [L("Mismatch: never reveal that decryption failed.", "Ασυμφωνία: ποτέ μην αποκαλύψεις ότι η αποκρυπτογράφηση απέτυχε."),
              L("Return the pseudo-random rejection key.", "Επέστρεψε το ψευδοτυχαίο κλειδί απόρριψης.")])],
     C.FO,
     L("Re-encrypt with ek, compare, and pick K′ or K̄ = J(z ‖ c). The reference uses an if; hardened code selects with a constant-time mask (cmov).",
       "Επανακρυπτογράφηση με ek, σύγκριση, και επιλογή K′ ή K̄ = J(z ‖ c). Η αναφορά χρησιμοποιεί if· ο hardened κώδικας επιλέγει με μάσκα σταθερού χρόνου (cmov)."),
     ref=True),

gaps("in-barrett", S_OPT,
     L("pq-crystals Barrett reduction: complete the shift.", "Αναγωγή Barrett του pq-crystals: συμπλήρωσε την ολίσθηση."),
     "c", """
int16_t barrett_reduce(int16_t a) {
    const int16_t v = ((1 << 26) + KYBER_Q / 2) / KYBER_Q;   /* 20159 */
    int16_t t = ((int32_t)v * a + (1 << 25)) >> [[0]];
    t *= KYBER_Q;
    return a - t;
}
""",
     [text(["26"], "reduction",
           [L("v approximates 2ᵏ/q; undo the same power of two.", "Το v προσεγγίζει το 2ᵏ/q· αναίρεσε την ίδια δύναμη του 2."),
            L("Match the exponent used to build v.", "Ταίριαξε τον εκθέτη που χρησιμοποιήθηκε για το v.")], width=4)],
     C.REDUCE,
     L("t = round(a·v / 2²⁶) ≈ a/q, so a − t·q is a's centred representative in [−(q−1)/2, (q−1)/2]. Tested on all 65536 inputs.",
       "t = round(a·v / 2²⁶) ≈ a/q, άρα το a − t·q είναι ο κεντραρισμένος αντιπρόσωπος του a στο [−(q−1)/2, (q−1)/2]. Ελέγχθηκε σε όλες τις 65536 εισόδους."),
     check="""
int main(void){
    for(int a=-32768;a<=32767;a++){
        int r=barrett_reduce((int16_t)a);
        if(((r-a)%KYBER_Q)!=0) return 1;
        if(r< -(KYBER_Q-1)/2 || r>(KYBER_Q-1)/2) return 2;
    }
    return 0;
}
"""),

gaps("in-montgomery", S_OPT,
     L("pq-crystals Montgomery reduction: a·2⁻¹⁶ mod q.", "Αναγωγή Montgomery του pq-crystals: a·2⁻¹⁶ mod q."),
     "c", """
#define QINV [[0]]   /* q^-1 mod 2^16, as int16 */
int16_t montgomery_reduce(int32_t a) {
    int16_t t = (int16_t)a * QINV;
    t = (a - (int32_t)t * KYBER_Q) >> [[1]];
    return t;
}
""",
     [choice(["-3327", "3327", "-3329"], 0, "reduction",
             [L("q·QINV must be ≡ 1 mod 2¹⁶.", "Το q·QINV πρέπει να είναι ≡ 1 mod 2¹⁶."),
              L("3329·x ≡ 1 (mod 65536), written as a signed 16-bit value.", "3329·x ≡ 1 (mod 65536), γραμμένο ως προσημασμένη τιμή 16 bits.")]),
      text(["16"], "reduction",
           [L("Montgomery divides by R exactly.", "Το Montgomery διαιρεί ακριβώς με το R."),
            L("R = 2¹⁶ here.", "Εδώ R = 2¹⁶.")], width=4)],
     C.REDUCE,
     L("t·q cancels the low 16 bits of a, so the shift by 16 is exact and the result is a·2⁻¹⁶ mod q, in (−q, q).",
       "Το t·q μηδενίζει τα χαμηλά 16 bits του a, άρα η ολίσθηση κατά 16 είναι ακριβής και το αποτέλεσμα είναι a·2⁻¹⁶ mod q, στο (−q, q)."),
     check="""
int main(void){
    const long R=65536, B=(long)KYBER_Q*32768;
    for(long a=-B;a<B;a+=997){
        int t=montgomery_reduce((int32_t)a);
        if(((long)t*R-a)%KYBER_Q!=0) return 1;
        if(t<=-KYBER_Q || t>=KYBER_Q) return 2;
    }
    return 0;
}
"""),
]
