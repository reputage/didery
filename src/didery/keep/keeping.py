# -*- encoding: utf-8 -*-
"""
Keeping Module

"""
from __future__ import generator_stop

import os
import stat
import shutil
from collections import OrderedDict as ODict, deque
import enum
import binascii

try:
    import simplejson as json
except ImportError:
    import json

try:
    import msgpack
except ImportError:
    pass

import libnacl

from ioflo.aid.sixing import *
from ioflo.aid import filing
from ioflo.aid import getConsole

from ..help.helping import setupTmpBaseDir, makeDid

console = getConsole()

KEEP_DIR_PATH = "/var/bluepea/keep"  # default
ALT_KEEP_DIR_PATH = os.path.join('~', '.indigo/bluepea/keep')

gKeepDirPath = None  # key directory location has not been set up yet
gKeeper = None  # Keeper instance has not been set up yet

class Keeper(object):
    """
    Keeper Class to manage or hold cryptographic Keys
    """
    KeepDir = os.path.join("/var", "bluepea", "keep", )
    AltKeepDir = os.path.join("~", ".indigo", "bluepea", "keep")
    Prefix = "key"
    Role = "server"
    Ext = "json" # default serialization type of json and msgpack
    Fields = ("seed", "sigkey", "verkey", "prikey", "pubkey")

    def __init__(self,
                 baseDirPath="",
                 prefix="",
                 role="",
                 ext="",
                 fields=None,
                 seed=None,
                 prikey=None,
                 **kwa):
        """
        Setup Keeper instance
        Create directories for saving associated data files
            keep/
                bluepea/
                    prefix.role.ext

        """
        if not baseDirPath:
            baseDirPath = self.KeepDir
        baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))

        if not os.path.exists(baseDirPath):
            try:
                os.makedirs(baseDirPath)
            except OSError as ex:
                baseDirPath = self.AltKeepDir
                baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
                if not os.path.exists(baseDirPath):
                    os.makedirs(baseDirPath)

        else:
            if not os.access(baseDirPath, os.R_OK | os.W_OK):
                baseDirPath = self.AltKeepDir
                baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
                if not os.path.exists(baseDirPath):
                    os.makedirs(baseDirPath)

        self.baseDirPath = baseDirPath

        self.prefix = prefix if prefix else self.Prefix
        self.role = role if role else self.Role
        self.ext = ext if ext else self.Ext

        self.filePath = os.path.join(self.baseDirPath,
                                     "{}.{}.{}".format(self.prefix,
                                                        self.role,
                                                        self.ext))

        if fields is None:
            fields = self.Fields
        self.fields = tuple(field for field in fields)

        for field in self.fields:
            if not hasattr(self, field):
                setattr(self, field, None)

        self.setupKeys(seed=seed, prikey=prikey)
        self.did = makeDid(self.verkey)  # create did

    def setupKeys(self, seed, prikey):
        """
        Override stored keys with seed or prikey as provided

        """
        self.loadKeys()
        if seed:
            self.seed = seed
            self.sigkey = None
            self.verkey = None

        if prikey:
            self.prikey = prikey
            self.pubkey = None

        self.refreshKeys()
        self.dumpKeys()

    def refreshKeys(self):
        """
        Refreshes keys as needed so valid set of keys
        """
        if not self.seed: # no signing key seed so create new one
            self.seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)

        if not self.sigkey or not self.verkey:  # ensure also sigkey and verkey
            self.verkey, self.sigkey = libnacl.crypto_sign_seed_keypair(self.seed)

        if not self.prikey: # no private encryption key so create new pair
            self.pubkey, self.prikey = libnacl.crypto_box_keypair()

        if not self.pubkey: # no public decryption key so create one from prikey
            self.pubkey = libnacl.crypto_scalarmult_base(self.prikey)

    def restoreKeys(self):
        """
        Reloads and refreshes as needed  and redumps  so valid set of keys
        """
        self.loadKeys()
        self.refreshKeys()
        self.dumpKeys()

    @staticmethod
    def dump(data, filePath):
        """
        Write data as as type self.ext to filepath. json or msgpack
        Sets permissions to only allow user to read and write to file
        """
        if " " in filePath:
            raise IOError("Invalid filepath '{0}' "
                                    "contains space".format(filePath))

        perm_other = stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH
        perm_group = stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP
        cumask = os.umask(perm_other | perm_group)  # save old into cumask and set new

        root, ext = os.path.splitext(filePath)
        if ext == '.json':
            with filing.ocfn(filePath, "w+") as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
        elif ext == '.msgpack':
            if not msgpack:
                raise IOError("Invalid filepath ext '{0}' "
                            "needs msgpack installed".format(filePath))
            with filing.ocfn(filePath, "w+b", binary=True) as f:
                msgpack.dump(data, f)
                f.flush()
                os.fsync(f.fileno())
        else:
            raise IOError("Invalid filepath ext '{0}' "
                        "not '.json' or '.msgpack'".format(filePath))

        os.umask(cumask)  # restore old

    @staticmethod
    def load(filePath):
        """
        Return data read from filepath as converted json or msgpack
        Otherwise return None
        """
        try:
            root, ext = os.path.splitext(filePath)
            if ext == '.json':
                with filing.ocfn(filePath, "r") as f:
                    it = json.load(f, object_pairs_hook=ODict)
            elif ext == '.msgpack':
                if not msgpack:
                    raise IOError("Invalid filepath ext '{0}' "
                                "needs msgpack installed".format(filePath))
                with filing.ocfn(filePath, "rb", binary=True) as f:
                    it = msgpack.load(f, object_pairs_hook=ODict)
            else:
                it = None
        except EOFError:
            return None
        except ValueError:
            return None
        return it

    @staticmethod
    def loadAllRoles(dirPath="", prefix="key", role=""):
        """
        Load and Return the keys dict indexed by role for all key data files with
        prefix in  directory at dirPath  both .json and .msgpack file extensions
        are supported

        If role is not empty then loads last keyfile that matches both prefix and role

        key files names of form:
        prefix.role.json
        prefix.role.msgpack

        (when prefix is the default "key" )
        key.server.json
        key.server.msgpack

        key fields in keyfiles should be in:
        ('seed', 'sigkey', 'verkey', 'prikey', 'pubkey')

        values are unicode hex format

        """
        roles = ODict()
        for fileName in os.listdir(dirPath):  # filenames without directory
            filePath = os.path.join(dirPath, fileName)  # need full path for isfile
            if not os.path.isfile(filePath):
                continue
            root, ext = os.path.splitext(fileName)
            if ext not in ['.json', '.msgpack']:
                continue
            pre, sep, rol = root.partition('.')
            if not rol or pre != prefix or (role and rol != role):
                continue
            roles[rol] = loadKeys(filePath)
        return roles

    def clearBaseDir(self):
        """
        Clear the base directory
        """
        if os.path.exists(self.baseDirPath):
            shutil.rmtree(self.baseDirPath)  # shutil.rmtree

    def verifyKeyFields(self, keys, fields=None):
        """
        Returns True if the fields in fields match the fields in keys
        """
        fields = fields if fields else self.fields
        return (set(fields) == set(keys.keys()))

    def dumpKeys(self):
        """
        Dump Keeper keys to file in .baseDirpath
        key values stored in unicode hex format
        """
        keys = ODict()
        for field in self.fields:
            if hasattr(self, field):
                keys[field] = binascii.hexlify(getattr(self, field)).decode('utf-8')
        self.dump(keys, self.filePath)

    def loadKeys(self):
        """
        Load and verify Keeper keys from .filePath if any
        """
        if not os.path.exists(self.filePath):
            return
        keys = self.load(self.filePath)
        for field in self.fields:
            if field in keys and hasattr(self, field):
                setattr(self, field, binascii.unhexlify(keys[field].encode('utf-8')))

# Utility Functions

def setupKeeper(baseDirPath=None, seed=None, prikey=None):
    """
    Setup  the module global gKeepDirPath and gKeeper using baseDirPath, seed,
    and prikey if provided otherwise use KEEP_DIR_PATH and restore new keys

    """
    global gKeepDirPath, gKeeper

    if not baseDirPath:
        baseDirPath = KEEP_DIR_PATH

    baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
    if not os.path.exists(baseDirPath):
        try:
            os.makedirs(baseDirPath)
        except OSError as ex:
            baseDirPath = ALT_KEEP_DIR_PATH
            baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
            if not os.path.exists(baseDirPath):
                os.makedirs(baseDirPath)
    else:
        if not os.access(baseDirPath, os.R_OK | os.W_OK):
            baseDirPath = ALT_KEEP_DIR_PATH
            baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
            if not os.path.exists(baseDirPath):
                os.makedirs(baseDirPath)

    gKeepDirPath = baseDirPath  # set global

    gKeeper = Keeper(baseDirPath=gKeepDirPath, seed=seed, prikey=prikey)

    return gKeeper

def setupTestKeeper():
    """
    Return gKeeper resulting from baseDirpath in temporary directory
    and then setupKeeper
    """
    seed = (b'\x0c\xaa\xc9\xc6G\x11\xf6nn\xd7\x1b7\xdc^i\xc5\x12O\xe9>\xe1$F\xe1'
            b'\xa4z\xd4\xb6P\xdd\x86\x1d')

    prikey = (b'\xd9\xc8<$\x03\xb9%\x03c\xb3*6g\xa7m\xd8\x8d\x08j\xd4^4\x88\xcac\xba\xd1\xe9'
              b'\xd9\xe6\x99%')

    baseDirPath = setupTmpBaseDir()
    baseDirPath = os.path.join(baseDirPath, "bluepea/keep")
    os.makedirs(baseDirPath)
    return setupKeeper(baseDirPath=baseDirPath, seed=seed, prikey=prikey)

def setupKeep(baseDirPath=None):
    """
    Setup  the module global gKeepDirPath using baseDirPath
    if provided otherwise use KEEP_DIR_PATH

    """
    global gKeepDirPath

    if not baseDirPath:
        baseDirPath = KEEP_DIR_PATH

    baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
    if not os.path.exists(baseDirPath):
        try:
            os.makedirs(baseDirPath)
        except OSError as ex:
            baseDirPath = ALT_DATABASE_DIR_PATH
            baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
            if not os.path.exists(baseDirPath):
                os.makedirs(baseDirPath)
    else:
        if not os.access(baseDirPath, os.R_OK | os.W_OK):
            baseDirPath = ALT_DATABASE_DIR_PATH
            baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
            if not os.path.exists(baseDirPath):
                os.makedirs(baseDirPath)

    gKeepDirPath = baseDirPath  # set global

    return gKeepDirPath

def setupTestKeep():
    """
    Return gKeepDirPath resulting from baseDirpath in temporary directory
    and then setupKeep
    """
    baseDirPath = setupTmpBaseDir()
    baseDirPath = os.path.join(baseDirPath, "bluepea/keep")
    os.makedirs(baseDirPath)
    return setupKeep(baseDirPath=baseDirPath)

def dumpKeys(data, filepath):
    """
    Write key data as as type self.ext to filepath. json or msgpack
    Sets permissions to only allow user to read and write to file
    """
    if " " in filepath:
        raise IOError("Invalid filepath '{0}' "
                                "contains space".format(filepath))

    perm_other = stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH
    perm_group = stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP
    cumask = os.umask(perm_other | perm_group)  # save old into cumask and set new

    root, ext = os.path.splitext(filepath)
    if ext == '.json':
        with filing.ocfn(filepath, "w+") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
    elif ext == '.msgpack':
        if not msgpack:
            raise IOError("Invalid filepath ext '{0}' "
                        "needs msgpack installed".format(filepath))
        with filing.ocfn(filepath, "w+b", binary=True) as f:
            msgpack.dump(data, f)
            f.flush()
            os.fsync(f.fileno())
    else:
        raise IOError("Invalid filepath ext '{0}' "
                    "not '.json' or '.msgpack'".format(filepath))

    os.umask(cumask)  # restore old


def loadKeys(filepath):
    """
    Return key data read from filepath as converted json
    Otherwise return None
    """
    try:
        root, ext = os.path.splitext(filepath)
        if ext == '.json':
            with filing.ocfn(filepath, "r") as f:
                it = json.load(f, object_pairs_hook=ODict)
        elif ext == '.msgpack':
            if not msgpack:
                raise IOError("Invalid filepath ext '{0}' "
                            "needs msgpack installed".format(filepath))
            with filing.ocfn(filepath, "rb", binary=True) as f:
                it = msgpack.load(f, object_pairs_hook=ODict)
        else:
            it = None
    except EOFError:
        return None
    except ValueError:
        return None
    return it

def loadAllKeyRoles(dirpath, prefix="key", role=""):
    """
    Load and Return the keys dict indexed by role for all key data files with
    prefix in  directory at dirpath  both .json and .msgpack file extensions
    are supported

    If role is not empty then loads last keyfile that matches both prefix and role

    key files names of form:
    prefix.role.json
    prefix.role.msgpack

    (when prefix is the default "key" )
    key.server.json
    key.server.msgpack

    key fields in keyfiles should be in:
    ('seed', 'sigkey', 'verkey', 'prikey', 'pubkey')

    values are bytes of binary key value

    """
    roles = ODict()
    for filename in os.listdir(dirpath):  # filenames without directory
        filepath = os.path.join(dirpath, filename)  # need full path for isfile
        if not os.path.isfile(filepath):
            continue
        root, ext = os.path.splitext(filename)
        if ext not in ['.json', '.msgpack']:
            continue
        pre, sep, rol = root.partition('.')
        if not rol or pre != prefix or (role and rol != role):
            continue
        roles[rol] = loadKeys(filepath)
    return roles
