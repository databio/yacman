import pytest
import yacman
import os

TEST_LIST = [
    ({"a": "1"}, {"a": ["alias_a"]}),
    ({"b": "1"}, {"b": ["alias_b"]}),
    ({"55": "1"}, {"55": ["alias_55"]})
]

TEST_LIST_MULTI = [
    ({"a": "1"}, {"a": ["alias_a", "a_a"]}),
    ({"b": "1"}, {"b": ["alias_b", "a_b"]}),
    ({"55": "1"}, {"55": ["alias_55", "a_55"]})
]


class TestAliases:
    @pytest.mark.parametrize(["entries", "aliases"], TEST_LIST)
    def test_aliases_init(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries, aliases=aliases)
        key = list(entries.keys())[0]
        alias = list(aliases.values())[0][0]
        assert x[key] == x[alias]

    @pytest.mark.parametrize(["entries", "aliases"], TEST_LIST)
    def test_aliases_setting(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_aliases(key=key, aliases=alias)
        assert x[key] == x[alias[0]]

    @pytest.mark.parametrize(["entries", "aliases"], TEST_LIST)
    def test_aliases_setting_append(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key][0]
        assert x.set_aliases(key=key, aliases=alias)
        assert x.set_aliases(key=key, aliases=alias + "_new")
        assert len(x.alias_dict[key]) == 2

    @pytest.mark.parametrize(["entries", "aliases"], TEST_LIST)
    def test_aliases_setting_overwrite(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key][0]
        assert x.set_aliases(key=key, aliases=alias)
        assert x.set_aliases(key=key, aliases=alias + "_new", overwrite=True)
        assert len(x.alias_dict[key]) == 1
        assert x.alias_dict[key] == [alias + "_new"]

    @pytest.mark.parametrize(["entries", "aliases"], TEST_LIST)
    def test_aliases_removal_all(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries, aliases=aliases)
        key = list(aliases.keys())[0]
        assert x.remove_aliases(key=key)
        assert key not in x.alias_dict.keys()

    # @pytest.mark.parametrize(["entries", "aliases"], TEST_LIST_MULTI)
    # def test_aliases_removal_multi_all(self, entries, aliases):
    #     x = yacman.AliasedYacAttMap(entries=entries, aliases=aliases)
    #     key = list(aliases.keys())[0]
    #     x.remove_aliases(key=key, aliases=aliases[key])
    #     assert key not in x.alias_dict.keys()

    @pytest.mark.parametrize(["entries", "aliases"], TEST_LIST)
    def test_accession_works_for_keys_and_aliases(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_aliases(key=key, aliases=alias)
        assert x[key] == x[alias[0]]

    @pytest.mark.parametrize(["entries", "aliases"], TEST_LIST)
    def test_containment_checks_for_keys_and_aliases(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_aliases(key=key, aliases=alias)
        assert key in x
        assert alias[0] in x


