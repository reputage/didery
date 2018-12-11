import pytest

from didery.did import didering


def didAssertions(did_reference,
                  did,
                  exp_scheme,
                  exp_method,
                  exp_idstring,
                  exp_query,
                  exp_path,
                  exp_fragment):
    """
    Tests a didery.did.didering.Did objects parsing of a DID

    :param did_reference: String
    :param did: didery.did.didering.Did object
    :param exp_scheme: String
    :param exp_method: String
    :param exp_idstring: String
    :param exp_query: String
    :param exp_path: String
    :param exp_fragment: String
    """

    assert exp_scheme == did.scheme
    assert exp_method == did.method
    assert exp_idstring == did.idString
    assert exp_query == did.query
    assert exp_path == did.path
    assert exp_fragment == did.fragment
    assert did.did_reference == did_reference
    assert did.did == "{}:{}:{}".format(exp_scheme, exp_method, exp_idstring)


def testBasicDid():
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=?color=blue/customers/1234#test_did"
    did = didering.Did(did_reference)
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = "color=blue"
    exp_path = "customers/1234"
    exp_fragment = "test_did"

    didAssertions(did_reference,
                  did,
                  exp_scheme,
                  exp_method,
                  exp_idstring,
                  exp_query,
                  exp_path,
                  exp_fragment)


def testMissingQueryDid():
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=/customers/1234#test_did"
    did = didering.Did(did_reference)
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = None
    exp_path = "customers/1234"
    exp_fragment = "test_did"

    didAssertions(did_reference,
                  did,
                  exp_scheme,
                  exp_method,
                  exp_idstring,
                  exp_query,
                  exp_path,
                  exp_fragment)


def testMissingPathDid():
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=?color=blue#test_did"
    did = didering.Did(did_reference)
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = "color=blue"
    exp_path = None
    exp_fragment = "test_did"

    didAssertions(did_reference,
                  did,
                  exp_scheme,
                  exp_method,
                  exp_idstring,
                  exp_query,
                  exp_path,
                  exp_fragment)


def testMissingFragmentDid():
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=?color=blue/customers/1234"
    did = didering.Did(did_reference)
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = "color=blue"
    exp_path = "customers/1234"
    exp_fragment = None

    didAssertions(did_reference,
                  did,
                  exp_scheme,
                  exp_method,
                  exp_idstring,
                  exp_query,
                  exp_path,
                  exp_fragment)


def testDIDOnlyDid():
    # No Query, Path, or Fragment
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    did = didering.Did(did_reference)
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = None
    exp_path = None
    exp_fragment = None

    didAssertions(did_reference,
                  did,
                  exp_scheme,
                  exp_method,
                  exp_idstring,
                  exp_query,
                  exp_path,
                  exp_fragment)


def testFragmentOnlyDid():
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=#test_did"
    did = didering.Did(did_reference)
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = None
    exp_path = None
    exp_fragment = "test_did"

    didAssertions(did_reference,
                  did,
                  exp_scheme,
                  exp_method,
                  exp_idstring,
                  exp_query,
                  exp_path,
                  exp_fragment)


def testQueryOnlyDid():
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=?color=blue"
    did = didering.Did(did_reference)
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = "color=blue"
    exp_path = None
    exp_fragment = None

    didAssertions(did_reference,
                  did,
                  exp_scheme,
                  exp_method,
                  exp_idstring,
                  exp_query,
                  exp_path,
                  exp_fragment)


def testPathOnlyDid():
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=/customers/1234"
    did = didering.Did(did_reference)
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = None
    exp_path = "customers/1234"
    exp_fragment = None

    didAssertions(did_reference,
                  did,
                  exp_scheme,
                  exp_method,
                  exp_idstring,
                  exp_query,
                  exp_path,
                  exp_fragment)


def testComplexIdstringWithoutReferenceDid():
    did_reference = "did:ala:quor:testnet1:QmeeasCZ9bjLbXhwFd7Fidz6CBziJQJpcUueBJ7d7csxhb"
    did = didering.Did(did_reference)
    exp_scheme = "did"
    exp_method = "ala"
    exp_idstring = "quor:testnet1:QmeeasCZ9bjLbXhwFd7Fidz6CBziJQJpcUueBJ7d7csxhb"
    exp_query = None
    exp_path = None
    exp_fragment = None

    didAssertions(did_reference,
                  did,
                  exp_scheme,
                  exp_method,
                  exp_idstring,
                  exp_query,
                  exp_path,
                  exp_fragment)


def testComplexIdstringWithReferenceDid():
    did_reference = "did:ala:quor:testnet1:QmeeasCZ9bjLbXhwFd7Fidz6CBziJQJpcUueBJ7d7csxhb?color=blue/customers/1234#test_did"
    did = didering.Did(did_reference)
    exp_scheme = "did"
    exp_method = "ala"
    exp_idstring = "quor:testnet1:QmeeasCZ9bjLbXhwFd7Fidz6CBziJQJpcUueBJ7d7csxhb"
    exp_query = "color=blue"
    exp_path = "customers/1234"
    exp_fragment = "test_did"

    didAssertions(did_reference,
                  did,
                  exp_scheme,
                  exp_method,
                  exp_idstring,
                  exp_query,
                  exp_path,
                  exp_fragment)


def testComplexQueryDid():
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=?color=blue&type=tshirt/customers/1234#test_did"
    did = didering.Did(did_reference)
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = "color=blue&type=tshirt"
    exp_path = "customers/1234"
    exp_fragment = "test_did"

    didAssertions(did_reference,
                  did,
                  exp_scheme,
                  exp_method,
                  exp_idstring,
                  exp_query,
                  exp_path,
                  exp_fragment)


def testEmptyDid():
    did_reference = ""

    with pytest.raises(ValueError) as ex:
        did = didering.Did(did_reference)
        assert ex.value == "Invalid DID value"


