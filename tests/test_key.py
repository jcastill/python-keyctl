
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from keyctl import KeyctlWrapper, KeyNotExistError, KeyAlreadyExistError, KeyctlOperationError
from keyctl import Key


# -------------------------------------------------------------------


@pytest.fixture
def empty_keyring():
    keyctl = KeyctlWrapper()

    keyctl.clear_keyring()
    keys = keyctl.get_all_key_ids()
    assert len(keys) == 0

    yield keyctl

    # teardown
    keyctl.clear_keyring()


# -------------------------------------------------------------------


class TestKey:
    def test_init(self, empty_keyring):
        # empty
        k = Key()
        assert k.id is None
        assert k.name is None
        assert k.data is None

        # non existing key
        with pytest.raises(KeyNotExistError):
            k = Key(999)

        # exisitng key
        keyctl = empty_keyring
        keyid = keyctl.add_key('test key', 'content xyz')
        k = Key(keyid)
        assert k.name == 'test key'
        assert k.data == 'content xyz'

    # ---------------------------------------------------------------

    def test_list(self, empty_keyring):
        keyctl = empty_keyring

        # empty list
        keylist = Key.list()
        assert len(keylist) == 0

        # 3 keys
        keysrc = [
            ['test key 1', 'content 111'],
            ['test key 2', 'content 222'],
            ['test key 3', 'content 333'],
        ]
        for src in keysrc:
            src.append(keyctl.add_key(src[0], src[1]))

        keylist = Key.list()
        assert len(keylist) == 3
        for i in range(0, 3):
            assert keylist[i].id == keysrc[i][2]
            assert keylist[i].name == keysrc[i][0]
            assert keylist[i].data == keysrc[i][1]

    # ---------------------------------------------------------------

    def test_search(self, empty_keyring):
        # non existing key
        with pytest.raises(KeyNotExistError):
            k = Key.search('this key does not exist')

        # existing key
        keyctl = empty_keyring
        keyid = keyctl.add_key('test key', 'content xyz')
        k = Key.search('test key')
        assert k.id == keyid
        assert k.name == 'test key'
        assert k.data == 'content xyz'

    # ---------------------------------------------------------------

    def test_add(self, empty_keyring):
        keyctl = empty_keyring

        # not existing key
        with pytest.raises(KeyNotExistError):
            keyctl.get_id_from_name('test key 111')

        k = Key.add('test key 111', 'content 111')
        keyid = keyctl.get_id_from_name('test key 111')
        assert k.id == keyid

        # already existing key
        with pytest.raises(KeyAlreadyExistError):
            Key.add('test key 111', 'content xyz')

    # ---------------------------------------------------------------

    def test_delete(self, empty_keyring):
        keyctl = empty_keyring

        # existing key
        keyid = keyctl.add_key('test key', 'abc')
        k = Key(keyid)
        assert k.name == 'test key'
        k.delete()
        with pytest.raises(KeyNotExistError):
            keyctl.get_id_from_name('test key')

        # uninitialized key
        k = Key()
        with pytest.raises(KeyctlOperationError):
            k.delete()

        # not existing key (delete called twice)
        keyid = keyctl.add_key('test key', 'abc')
        k = Key(keyid)
        k.delete()
        with pytest.raises(KeyNotExistError):
            k.delete()

    # ---------------------------------------------------------------

    def test_update(self, empty_keyring):
        keyctl = empty_keyring

        # existing key
        keyid = keyctl.add_key('test key', 'abc')
        k1 = Key(keyid)
        assert k1.data == 'abc'

        k1.update('xyz')
        assert k1.data == 'xyz'
        k2 = Key(keyid)
        assert k1.id == k2.id
        assert k1.name == k2.name
        assert 'xyz' == k2.data

        # not existing key
        k1.delete()
        with pytest.raises(KeyNotExistError):
            k2.update('xxxx')




# -------------------------------------------------------------------