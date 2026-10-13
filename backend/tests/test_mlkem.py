"""
app/services/mlkem.py against the C reference, byte for byte, for k = 2, 3, 4.
Runs with pytest or plain `python3 tests/test_mlkem.py`. Needs gcc for the
cross-check; the other tests run without it.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app.services import mlkem  # noqa: E402

REF_C = os.path.join(ROOT, "tests", "data", "kyber_fips203_update.c")

DRIVER = r"""
static void hexout(const char*tag,const uint8_t*p,size_t n){
    printf("%s ",tag); for(size_t i=0;i<n;i++) printf("%02x",p[i]); printf("\n");
}
int main(int argc,char**argv){
    uint8_t d[32],z[32],m[32];
    for(int i=0;i<32;i++){ d[i]=(uint8_t)strtol((char[]){argv[1][2*i],argv[1][2*i+1],0},0,16);
                           z[i]=(uint8_t)strtol((char[]){argv[2][2*i],argv[2][2*i+1],0},0,16);
                           m[i]=(uint8_t)strtol((char[]){argv[3][2*i],argv[3][2*i+1],0},0,16); }
    uint8_t ek[PKE_PK_BYTES],dk[DK_BYTES],ct[CT_BYTES],Ka[32],Kb[32],Kr[32];
    mlkem_keygen(d,z,ek,dk); mlkem_encaps(ek,m,Ka,ct); mlkem_decaps(dk,ct,Kb);
    ct[0]^=0xFF; mlkem_decaps(dk,ct,Kr); ct[0]^=0xFF;
    hexout("ek",ek,PKE_PK_BYTES); hexout("dk",dk,DK_BYTES); hexout("ct",ct,CT_BYTES);
    hexout("K",Ka,32); hexout("K2",Kb,32); hexout("Kr",Kr,32);
    return 0;
}
"""

SEEDS = [
    (bytes(range(32)), bytes(range(32, 64)), bytes(range(64, 96))),
    (hashlib.sha3_256(b"d").digest(), hashlib.sha3_256(b"z").digest(), hashlib.sha3_256(b"m").digest()),
]


def run_c(k: int, d: bytes, z: bytes, m: bytes) -> dict[str, bytes]:
    with open(REF_C, encoding="utf-8") as f:
        src = f.read().replace("#define KYBER_K 2 ", f"#define KYBER_K {k} ")
    with tempfile.TemporaryDirectory() as tmp:
        c_path, exe = os.path.join(tmp, "ref.c"), os.path.join(tmp, "ref")
        with open(c_path, "w") as f:
            f.write("#include <stdlib.h>\n" + src.replace("int main(void){", "int ref_main(void){") + DRIVER)
        subprocess.run(["gcc", "-O2", "-o", exe, c_path], check=True, capture_output=True)
        out = subprocess.run([exe, d.hex(), z.hex(), m.hex()], check=True, capture_output=True, text=True).stdout
    return {tag: bytes.fromhex(val) for tag, val in (line.split() for line in out.strip().splitlines())}


def test_matches_c_reference_byte_for_byte():
    if not (shutil.which("gcc") and os.path.exists(REF_C)):
        print("SKIP: gcc or reference missing")
        return
    for k in (2, 3, 4):
        for d, z, m in SEEDS:
            ref = run_c(k, d, z, m)
            ek, dk = mlkem.keygen(k, d, z)
            K, ct = mlkem.encaps(k, ek, m)
            bad = bytes([ct[0] ^ 0xFF]) + ct[1:]
            assert ek == ref["ek"], f"ek differs for k={k}"
            assert dk == ref["dk"], f"dk differs for k={k}"
            assert ct == ref["ct"], f"ct differs for k={k}"
            assert K == ref["K"] == ref["K2"] == mlkem.decaps(k, dk, ct), f"K differs for k={k}"
            assert mlkem.decaps(k, dk, bad) == ref["Kr"], f"rejection key differs for k={k}"


def test_documented_fingerprint_512():
    # full_code/future_update.md: the C demo seed gives an ML-KEM-512 ek whose
    # first bytes are c78209ae (the broken-Keccak build gave 9f6b8b41).
    d = bytes([0x7f, 0x9c, 0x2b, 0xa4, 0xe8, 0x8f, 0x82, 0x7d, 0x61, 0x60, 0x45, 0x07, 0xa7, 0x33, 0x87, 0x12,
               0x10, 0x50, 0x40, 0x05, 0x6f, 0xe8, 0x3b, 0x57, 0x11, 0x89, 0x20, 0xc2, 0x65, 0x23, 0x41, 0x00])
    z = bytes(0xA0 + i for i in range(32))
    ek, _ = mlkem.keygen(2, d, z)
    assert ek.hex().startswith("c78209ae"), ek[:8].hex()


def test_sizes_roundtrip_and_rejection():
    expected = {2: (800, 1632, 768), 3: (1184, 2400, 1088), 4: (1568, 3168, 1568)}
    for k, (e, dsz, c) in expected.items():
        ek, dk = mlkem.keygen(k, os.urandom(32), os.urandom(32))
        K, ct = mlkem.encaps(k, ek, os.urandom(32))
        assert (len(ek), len(dk), len(ct)) == (e, dsz, c) == tuple(mlkem.sizes(k)[x] for x in ("ek", "dk", "ct"))
        assert mlkem.decaps(k, dk, ct) == K
        bad = ct[:-1] + bytes([ct[-1] ^ 1])
        assert mlkem.decaps(k, dk, bad) != K


def test_ntt_roundtrip_and_basemul():
    import random
    rnd = random.Random(1)
    for _ in range(5):
        a = [rnd.randrange(mlkem.Q) for _ in range(mlkem.N)]
        b = [rnd.randrange(mlkem.Q) for _ in range(mlkem.N)]
        assert mlkem.intt(mlkem.ntt(a)) == a
        school = [0] * mlkem.N
        for i in range(mlkem.N):
            for j in range(mlkem.N):
                kk, p = i + j, a[i] * b[j]
                if kk < mlkem.N:
                    school[kk] += p
                else:
                    school[kk - mlkem.N] -= p
        assert mlkem.intt(mlkem.basemul(mlkem.ntt(a), mlkem.ntt(b))) == [x % mlkem.Q for x in school]


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok  ", name)
            except AssertionError as e:
                failed += 1
                print("FAIL", name, e)
    print(f"{failed} failed")
    sys.exit(1 if failed else 0)
