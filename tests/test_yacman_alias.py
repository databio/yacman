import pytest
import yacman
from yacman.exceptions import AliasError


class TestAliases:
    @pytest.mark.parametrize(
        "entries, aliases",
        [
            ({"a": "1"}, {"a": ["alias_a"]}),
            ({"b": "1"}, {"b": ["alias_b"]}),
            ({"55": "1"}, {"55": ["alias_55"]}),
        ],
    )
    def test_aliases_init(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries, aliases=aliases)
        key = list(entries.keys())[0]
        alias = list(aliases.values())[0][0]
        assert x[key] == x[alias]

    @pytest.mark.parametrize(
        ["entries", "aliases"],
        [
            ({"a": "1"}, {"a": ["alias_a"]}),
            ({"b": "1"}, {"b": ["alias_b"]}),
            ({"55": "1"}, {"55": ["alias_55"]}),
        ],
    )
    def test_aliases_init_valid_fun(self, entries, aliases):
        print(f"aliases: {aliases}")

        def _aliases_fun(x):
            return aliases

        yacman.AliasedYacAttMap(entries=entries, aliases=_aliases_fun)

    @pytest.mark.parametrize(
        ["entries", "aliases"],
        [
            ({"a": "1"}, {"a": ["alias_a"]}),
            ({"b": "1"}, {"b": ["alias_b"]}),
            ({"55": "1"}, {"55": ["alias_55"]}),
        ],
    )
    def test_aliases_init_invalid_fun(self, entries, aliases):
        print(f"aliases: {aliases}")

        def _aliases_fun():
            return aliases

        with pytest.raises(AliasError):
            yacman.AliasedYacAttMap(
                entries=entries, aliases=_aliases_fun, aliases_strict=True
            )

    @pytest.mark.parametrize(
        ["entries", "aliases"],
        [
            ({"a": "1"}, {"a": ["alias_a"]}),
            ({"b": "1"}, {"b": ["alias_b"]}),
            ({"55": "1"}, {"55": ["alias_55"]}),
        ],
    )
    def test_aliases_init_fun_error(self, entries, aliases):
        print(f"aliases: {aliases}")

        def _aliases_fun():
            raise Exception("test")

        with pytest.raises(AliasError):
            yacman.AliasedYacAttMap(
                entries=entries, aliases=_aliases_fun, aliases_strict=True
            )

    @pytest.mark.parametrize(
        ["entries", "aliases"],
        [
            ({"a": "1"}, {"a": ["alias_a"]}),
            ({"b": "1"}, {"b": ["alias_b"]}),
            ({"55": "1"}, {"55": ["alias_55"]}),
        ],
    )
    def test_aliases_init_fun_returns_invalid(self, entries, aliases):
        print(f"aliases: {aliases}")

        def _aliases_fun():
            return {"a": "test"}

        with pytest.raises(AliasError):
            yacman.AliasedYacAttMap(
                entries=entries, aliases=_aliases_fun, aliases_strict=True
            )

    @pytest.mark.parametrize(
        ["entries", "aliases"],
        [
            ({"a": "1"}, {"a": ["alias_a"]}),
            ({"b": "1"}, {"b": ["alias_b"]}),
            ({"55": "1"}, {"55": ["alias_55"]}),
        ],
    )
    def test_aliases_setting(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_aliases(key=key, aliases=alias)
        assert x[key] == x[alias[0]]

    @pytest.mark.parametrize(
        ["entries", "aliases"],
        [
            ({"a": "1"}, {"a": ["alias_a"]}),
            ({"b": "1"}, {"b": ["alias_b"]}),
            ({"55": "1"}, {"55": ["alias_55"]}),
        ],
    )
    def test_aliases_setting_reset(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key][0]
        assert x.set_aliases(key=key, aliases=alias)
        assert x.set_aliases(key=key, aliases=alias + "_new", reset_key=True)
        assert x[alias + "_new"] == x[key]
        with pytest.raises(KeyError):
            x[alias]

    @pytest.mark.parametrize(
        ["entries", "aliases"],
        [
            ({"a": "1"}, {"a": ["alias_a"]}),
            ({"b": "1"}, {"b": ["alias_b"]}),
            ({"55": "1"}, {"55": ["alias_55"]}),
        ],
    )
    def test_aliases_setting_no_overwrite(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key][0]
        assert x.set_aliases(key=key, aliases=alias)
        set_al, removed_al = x.set_aliases(key=key + "_new", aliases=alias)
        assert not set_al
        assert x[alias] == x[key]

    @pytest.mark.parametrize(
        ["entries", "aliases"],
        [
            ({"a": "1"}, {"a": ["alias_a"]}),
            ({"b": "1"}, {"b": ["alias_b"]}),
            ({"55": "1"}, {"55": ["alias_55"]}),
        ],
    )
    def test_aliases_setting_overwrite(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key][0]

        assert x.set_aliases(key=key, aliases=alias)
        set_al, removed_al = x.set_aliases(
            key=key + "_new", aliases=alias, overwrite=True
        )
        assert len(set_al) > 0
        with pytest.raises(KeyError):
            x[alias]

    @pytest.mark.parametrize(
        ["entries", "aliases"],
        [
            ({"a": "1"}, {"a": ["alias_a"]}),
            ({"b": "1"}, {"b": ["alias_b"]}),
            ({"55": "1"}, {"55": ["alias_55"]}),
        ],
    )
    def test_aliases_removal_all(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries, aliases=aliases)
        key = list(aliases.keys())[0]
        removed = x.remove_aliases(key=key)
        assert isinstance(removed, list)
        assert len(removed) == 1
        with pytest.raises(yacman.UndefinedAliasError):
            x.get_aliases(key)

    @pytest.mark.parametrize(
        ["entries", "aliases"],
        [
            ({"a": "1"}, {"a": ["alias_a", "alias_a1"]}),
            ({"b": "1"}, {"b": ["alias_b", "alias_b1"]}),
            ({"55": "1"}, {"55": ["alias_55", "alias_551"]}),
        ],
    )
    def test_aliases_removal_specific(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries, aliases=aliases)
        key = list(aliases.keys())[0]
        alias_to_remove = [aliases[key][0]]
        removed = x.remove_aliases(key=key, aliases=alias_to_remove)
        assert isinstance(removed, list)
        assert removed == alias_to_remove

    @pytest.mark.parametrize(
        ["entries", "aliases"],
        [
            ({"a": "1"}, {"a": ["alias_a"]}),
            ({"b": "1"}, {"b": ["alias_b"]}),
            ({"55": "1"}, {"55": ["alias_55"]}),
        ],
    )
    def test_accession_works_for_keys_and_aliases(self, entries, aliases):
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_aliases(key=key, aliases=alias)
        assert x[key] == x[alias[0]]

    @pytest.mark.parametrize(
        ["entries", "aliases"],
        [
            ({"a": "1"}, {"a": ["alias_a"]}),
            ({"b": "1"}, {"b": ["alias_b"]}),
            ({"55": "1"}, {"55": ["alias_55"]}),
        ],
    )
    def test_containment_checks_for_keys_and_aliases(self, entries, aliases):
        print(f"aliases: {aliases}")
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_aliases(key=key, aliases=alias)
        assert key in x
        assert alias[0] in x

    @pytest.mark.parametrize(
        ["entries", "aliases"],
        [
            ({"a": "1"}, {"a": ["alias_a"]}),
            ({"b": "1"}, {"b": ["alias_b"]}),
            ({"55": "1"}, {"55": ["alias_55"]}),
        ],
    )
    def test_delitem_checks_for_keys_and_aliases(self, entries, aliases):
        print(f"aliases: {aliases}")
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        x.__delitem__(key)
        assert key not in x
        x = yacman.AliasedYacAttMap(entries=entries)
        x.set_aliases(key=key, aliases=alias)
        x.__delitem__(alias[0])
        assert key not in x

    @pytest.mark.parametrize(
        ["entries", "aliases"],
        [
            ({"a": "1"}, {"a": ["alias_a"]}),
            ({"b": "1"}, {"b": ["alias_b"]}),
            ({"55": "1"}, {"55": ["alias_55"]}),
        ],
    )
    def test_containment_correctly_resolves_to_false(self, entries, aliases):
        print(f"aliases: {aliases}")
        x = yacman.AliasedYacAttMap(entries=entries)
        key = list(aliases.keys())[0]
        alias = aliases[key]
        assert x.set_aliases(key=key, aliases=alias)
        assert not (f"{key}_false" in x)
        assert not (f"{alias[0]}_false" in x)
