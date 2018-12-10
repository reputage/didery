import pytest

from didery.did import didering


def testBasicExtractDidParts():
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=?color=blue/customers/1234#test_did"
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = "color=blue"
    exp_path = "customers/1234"
    exp_fragment = "test_did"

    scheme, method, idstring, query, path, fragment = didering.extractDidParts(did_reference)

    assert exp_scheme == scheme
    assert exp_method == method
    assert exp_idstring == idstring
    assert exp_query == query
    assert exp_path == path
    assert exp_fragment == fragment


def testMissingQueryExtractDidParts():
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=/customers/1234#test_did"
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = None
    exp_path = "customers/1234"
    exp_fragment = "test_did"

    scheme, method, idstring, query, path, fragment = didering.extractDidParts(did_reference)

    assert exp_scheme == scheme
    assert exp_method == method
    assert exp_idstring == idstring
    assert exp_query == query
    assert exp_path == path
    assert exp_fragment == fragment


def testMissingPathExtractDidParts():
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=?color=blue#test_did"
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = "color=blue"
    exp_path = None
    exp_fragment = "test_did"

    scheme, method, idstring, query, path, fragment = didering.extractDidParts(did_reference)

    assert exp_scheme == scheme
    assert exp_method == method
    assert exp_idstring == idstring
    assert exp_query == query
    assert exp_path == path
    assert exp_fragment == fragment


def testMissingFragmentExtractDidParts():
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=?color=blue/customers/1234"
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = "color=blue"
    exp_path = "customers/1234"
    exp_fragment = None

    scheme, method, idstring, query, path, fragment = didering.extractDidParts(did_reference)

    assert exp_scheme == scheme
    assert exp_method == method
    assert exp_idstring == idstring
    assert exp_query == query
    assert exp_path == path
    assert exp_fragment == fragment


def testDIDOnlyExtractDidParts():
    # No Query, Path, or Fragment
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = None
    exp_path = None
    exp_fragment = None

    scheme, method, idstring, query, path, fragment = didering.extractDidParts(did_reference)

    assert exp_scheme == scheme
    assert exp_method == method
    assert exp_idstring == idstring
    assert exp_query == query
    assert exp_path == path
    assert exp_fragment == fragment


def testFragmentOnlyExtractDidParts():
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=#test_did"
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = None
    exp_path = None
    exp_fragment = "test_did"

    scheme, method, idstring, query, path, fragment = didering.extractDidParts(did_reference)

    assert exp_scheme == scheme
    assert exp_method == method
    assert exp_idstring == idstring
    assert exp_query == query
    assert exp_path == path
    assert exp_fragment == fragment


def testQueryOnlyExtractDidParts():
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=?color=blue"
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = "color=blue"
    exp_path = None
    exp_fragment = None

    scheme, method, idstring, query, path, fragment = didering.extractDidParts(did_reference)

    assert exp_scheme == scheme
    assert exp_method == method
    assert exp_idstring == idstring
    assert exp_query == query
    assert exp_path == path
    assert exp_fragment == fragment


def testPathOnlyExtractDidParts():
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=/customers/1234"
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = None
    exp_path = "customers/1234"
    exp_fragment = None

    scheme, method, idstring, query, path, fragment = didering.extractDidParts(did_reference)

    assert exp_scheme == scheme
    assert exp_method == method
    assert exp_idstring == idstring
    assert exp_query == query
    assert exp_path == path
    assert exp_fragment == fragment


def testComplexIdstringDidOnlyExtractDidParts():
    did_reference = "did:ala:quor:testnet1:QmeeasCZ9bjLbXhwFd7Fidz6CBziJQJpcUueBJ7d7csxhb"
    exp_scheme = "did"
    exp_method = "ala"
    exp_idstring = "quor:testnet1:QmeeasCZ9bjLbXhwFd7Fidz6CBziJQJpcUueBJ7d7csxhb"
    exp_query = None
    exp_path = None
    exp_fragment = None

    scheme, method, idstring, query, path, fragment = didering.extractDidParts(did_reference)

    assert exp_scheme == scheme
    assert exp_method == method
    assert exp_idstring == idstring
    assert exp_query == query
    assert exp_path == path
    assert exp_fragment == fragment


def testComplexIdstringExtractDidParts():
    did_reference = "did:ala:quor:testnet1:QmeeasCZ9bjLbXhwFd7Fidz6CBziJQJpcUueBJ7d7csxhb?color=blue/customers/1234#test_did"
    exp_scheme = "did"
    exp_method = "ala"
    exp_idstring = "quor:testnet1:QmeeasCZ9bjLbXhwFd7Fidz6CBziJQJpcUueBJ7d7csxhb"
    exp_query = "color=blue"
    exp_path = "customers/1234"
    exp_fragment = "test_did"

    scheme, method, idstring, query, path, fragment = didering.extractDidParts(did_reference)

    assert exp_scheme == scheme
    assert exp_method == method
    assert exp_idstring == idstring
    assert exp_query == query
    assert exp_path == path
    assert exp_fragment == fragment


def testComplexQueryExtractDidParts():
    did_reference = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=?color=blue&type=tshirt/customers/1234#test_did"
    exp_scheme = "did"
    exp_method = "dad"
    exp_idstring = "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    exp_query = "color=blue&type=tshirt"
    exp_path = "customers/1234"
    exp_fragment = "test_did"

    scheme, method, idstring, query, path, fragment = didering.extractDidParts(did_reference)

    assert exp_scheme == scheme
    assert exp_method == method
    assert exp_idstring == idstring
    assert exp_query == query
    assert exp_path == path
    assert exp_fragment == fragment


def testEmptyExtractDidParts():
    did_reference = ""

    with pytest.raises(ValueError) as ex:
        scheme, method, idstring, query, path, fragment = didering.extractDidParts(did_reference)
        assert ex.value == "Invalid DID value"

