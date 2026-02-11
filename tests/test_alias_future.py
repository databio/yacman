import pytest

import yacman
from yacman import AliasedYAMLConfigManager
from yacman.exceptions import AliasError, UndefinedAliasError

ENTRIES_ALIASES_PARAMS = [
    ({"a": "1"}, {"a": ["alias_a"]}),
    ({"b": "1"}, {"b": ["alias_b"]}),
    ({"55": "1"}, {"55": ["alias_55"]}),
]


class TestAliasedYAMLConfigManager:
    @pytest.mark.parametrize("entries, aliases", ENTRIES_ALIASES_PARAMS)
    def test_init_with_aliases(self, entries, aliases):
        x = AliasedYAMLConfigManager(entries=entries, aliases=aliases)
        key = list(entries.keys())[0]
        alias = list(aliases.values())[0][0]
        assert x[key] == x[alias]

    @pytest.mark.parametrize("entries, aliases", ENTRIES_ALIASES_PARAMS)
    def test_init_with_callable_aliases(self, entries, aliases):
        def _aliases_fun(x):
            return aliases

        x = AliasedYAMLConfigManager(entries=entries, aliases=_aliases_fun)
        key = list(entries.keys())[0]
        alias = list(aliases.values())[0][0]
        assert x[key] == x[alias]

    @pytest.mark.parametrize("entries, aliases", ENTRIES_ALIASES_PARAMS)
    def test_init_invalid_callable_raises(self, entries, aliases):
        def _aliases_fun():
            return aliases

        with pytest.raises(AliasError):
            AliasedYAMLConfigManager(
                entries=entries, aliases=_aliases_fun, aliases_strict=True
            )

    @pytest.mark.parametrize("entries, aliases", ENTRIES_ALIASES_PARAMS)
    def test_init_callable_error_raises(self, entries, aliases):
        def _aliases_fun():
            raise Exception("test")

        with pytest.raises(AliasError):
            AliasedYAMLConfigManager(
                entries=entries, aliases=_aliases_fun, aliases_strict=True
            )

    @pytest.mark.parametrize("entries, aliases", ENTRIES_ALIASES_PARAMS)
    def test_init_callable_returns_invalid(self, entries, aliases):
        def _aliases_fun():
            return {"a": "test"}

        with pytest.raises(AliasError):
            AliasedYAMLConfigManager(
                entries=entries, aliases=_aliases_fun, aliases_strict=True
            )

    @pytest.mark.parametrize("entries, aliases", ENTRIES_ALIASES_PARAMS)
    def test_set_aliases(self, entries, aliases):
        x = AliasedYAMLConfigManager(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_aliases(key=key, aliases=alias)
        assert x[key] == x[alias[0]]

    @pytest.mark.parametrize("entries, aliases", ENTRIES_ALIASES_PARAMS)
    def test_set_aliases_reset(self, entries, aliases):
        x = AliasedYAMLConfigManager(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key][0]
        assert x.set_aliases(key=key, aliases=alias)
        assert x.set_aliases(key=key, aliases=alias + "_new", reset_key=True)
        assert x[alias + "_new"] == x[key]
        with pytest.raises(KeyError):
            x[alias]

    @pytest.mark.parametrize("entries, aliases", ENTRIES_ALIASES_PARAMS)
    def test_set_aliases_no_overwrite(self, entries, aliases):
        x = AliasedYAMLConfigManager(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key][0]
        assert x.set_aliases(key=key, aliases=alias)
        set_al, removed_al = x.set_aliases(key=key + "_new", aliases=alias)
        assert not set_al
        assert x[alias] == x[key]

    @pytest.mark.parametrize("entries, aliases", ENTRIES_ALIASES_PARAMS)
    def test_set_aliases_overwrite(self, entries, aliases):
        x = AliasedYAMLConfigManager(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key][0]
        assert x.set_aliases(key=key, aliases=alias)
        set_al, removed_al = x.set_aliases(
            key=key + "_new", aliases=alias, overwrite=True
        )
        assert len(set_al) > 0
        with pytest.raises(KeyError):
            x[alias]

    @pytest.mark.parametrize("entries, aliases", ENTRIES_ALIASES_PARAMS)
    def test_remove_aliases_all(self, entries, aliases):
        x = AliasedYAMLConfigManager(entries=entries, aliases=aliases)
        key = list(aliases.keys())[0]
        removed = x.remove_aliases(key=key)
        assert isinstance(removed, list)
        assert len(removed) == 1
        with pytest.raises(UndefinedAliasError):
            x.get_aliases(key)

    @pytest.mark.parametrize(
        "entries, aliases",
        [
            ({"a": "1"}, {"a": ["alias_a", "alias_a1"]}),
            ({"b": "1"}, {"b": ["alias_b", "alias_b1"]}),
            ({"55": "1"}, {"55": ["alias_55", "alias_551"]}),
        ],
    )
    def test_remove_aliases_specific(self, entries, aliases):
        x = AliasedYAMLConfigManager(entries=entries, aliases=aliases)
        key = list(aliases.keys())[0]
        alias_to_remove = [aliases[key][0]]
        removed = x.remove_aliases(key=key, aliases=alias_to_remove)
        assert isinstance(removed, list)
        assert removed == alias_to_remove

    @pytest.mark.parametrize("entries, aliases", ENTRIES_ALIASES_PARAMS)
    def test_accession_by_key_and_alias(self, entries, aliases):
        x = AliasedYAMLConfigManager(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_aliases(key=key, aliases=alias)
        assert x[key] == x[alias[0]]

    @pytest.mark.parametrize("entries, aliases", ENTRIES_ALIASES_PARAMS)
    def test_containment_by_key_and_alias(self, entries, aliases):
        x = AliasedYAMLConfigManager(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_aliases(key=key, aliases=alias)
        assert key in x
        assert alias[0] in x

    @pytest.mark.parametrize("entries, aliases", ENTRIES_ALIASES_PARAMS)
    def test_delitem_by_key_and_alias(self, entries, aliases):
        x = AliasedYAMLConfigManager(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        del x[key]
        assert key not in x
        x = AliasedYAMLConfigManager(entries=entries)
        x.set_aliases(key=key, aliases=alias)
        del x[alias[0]]
        assert key not in x

    @pytest.mark.parametrize("entries, aliases", ENTRIES_ALIASES_PARAMS)
    def test_containment_false_for_missing(self, entries, aliases):
        x = AliasedYAMLConfigManager(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_aliases(key=key, aliases=alias)
        assert f"{key}_false" not in x
        assert f"{alias[0]}_false" not in x

    def test_get_key_raises_for_undefined(self):
        x = AliasedYAMLConfigManager(entries={"a": "1"})
        with pytest.raises(UndefinedAliasError):
            x.get_key("nonexistent")

    def test_get_aliases_raises_for_undefined(self):
        x = AliasedYAMLConfigManager(entries={"a": "1"})
        with pytest.raises(UndefinedAliasError):
            x.get_aliases("a")

    def test_exact_mode_ignores_aliases(self):
        x = AliasedYAMLConfigManager(
            entries={"a": "1"}, aliases={"a": ["alias_a"]}, exact=True
        )
        with pytest.raises(KeyError):
            x["alias_a"]

    def test_is_mutable_mapping(self):
        x = AliasedYAMLConfigManager(entries={"a": "1"})
        x["b"] = "2"
        assert x["b"] == "2"
        assert len(x) == 2
        assert list(x) == ["a", "b"]


class TestLockedProperty:
    def test_locked_without_locker(self):
        x = yacman.YAMLConfigManager(entries={"a": "1"})
        assert x.locked is False

    def test_settings_property(self):
        x = yacman.YAMLConfigManager(entries={"a": "1"})
        s = x.settings
        assert "locked" in s
        assert s["locked"] is False
