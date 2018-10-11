import didery.help.sig_validation as valid
from fastecdsa import keys, curve


def test():
    sk, pk = keys.gen_keypair(curve.secp256k1)

    assert False
