import pytest
import yacman
import os


class TestAliases:
    @pytest.mark.parametrize(["entries", "aliases"],
                             [({"a": "1"}, {"a": "alias_a"}),
                              ({"b": "1"}, {"b": "alias_b"}),
                              ({"55": "1"}, {"55": "alias_55"})])
    def test_aliases_init(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries, aliases=aliases)
        key = list(entries.keys())[0]
        alias = list(aliases.keys())[0]
        assert x[key] == x[alias]

    @pytest.mark.parametrize(["entries", "aliases"],
                             [({"a": "1"}, {"a": "alias_a"}),
                              ({"b": "1"}, {"b": "alias_b"}),
                              ({"55": "1"}, {"55": "alias_55"})])
    def test_aliases_setting(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_alias(key=key, alias=alias)
        assert x[key] == x[alias]

    @pytest.mark.parametrize(["entries", "aliases"],
                             [({"a": "1"}, {"a": "alias_a"}),
                              ({"b": "1"}, {"b": "alias_b"}),
                              ({"55": "1"}, {"55": "alias_55"})])
    def test_aliases_setting_preserve(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_alias(key=key, alias=alias)
        assert not x.set_alias(key=key, alias=alias + "_new")
        assert x[key] == x[alias]

    @pytest.mark.parametrize(["entries", "aliases"],
                             [({"a": "1"}, {"a": "alias_a"}),
                              ({"b": "1"}, {"b": "alias_b"}),
                              ({"55": "1"}, {"55": "alias_55"})])
    def test_aliases_setting_overwrite(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_alias(key=key, alias=alias)
        assert x.set_alias(key=key, alias=alias + "_new", force=True)
        with pytest.raises(KeyError):
            x[alias]
        assert x[key] == x[alias + "_new"]

    @pytest.mark.parametrize(["entries", "aliases"],
                             [({"a": "1"}, {"a": "alias_a"}),
                              ({"b": "1"}, {"b": "alias_b"}),
                              ({"55": "1"}, {"55": "alias_55"})])
    def test_aliases_removal(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_alias(key=key, alias=alias)
        assert x.remove_alias(key=key)
        assert key not in x.alias_dict.keys()

    @pytest.mark.parametrize(["entries", "aliases"],
                             [({"a": "1"}, {"a": "alias_a"}),
                              ({"b": "1"}, {"b": "alias_b"}),
                              ({"55": "1"}, {"55": "alias_55"})])
    def test_accession_works_for_keys_and_aliases(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_alias(key=key, alias=alias)
        assert x[key] == x[alias]

    @pytest.mark.parametrize(["entries", "aliases"],
                             [({"a": "1"}, {"a": "alias_a"}),
                              ({"b": "1"}, {"b": "alias_b"}),
                              ({"55": "1"}, {"55": "alias_55"})])
    def test_containment_checks_for_keys_and_aliases(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_alias(key=key, alias=alias)
        assert key in x
        assert alias in x


