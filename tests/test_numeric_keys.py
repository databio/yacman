"""Tests for numeric key handling in YAML files."""

import pytest
from yacman import YAMLConfigManager


class TestNumericKeys:
    """Test that numeric keys in YAML are converted to strings."""

    def test_numeric_keys_are_strings(self, tmp_path):
        """Test that numeric keys like 2 and 3.14 become '2' and '3.14'."""
        # Create a YAML file with numeric keys
        yaml_file = tmp_path / "numeric.yaml"
        yaml_file.write_text(
            """
2: second
3.14: pi
"4": four_string
text: regular_value
"""
        )

        # Load it with YAMLConfigManager (convert Path to str for locking)
        ym = YAMLConfigManager.from_yaml_file(str(yaml_file))

        # Keys should all be strings
        assert "2" in ym
        assert "3.14" in ym
        assert "4" in ym
        assert "text" in ym

        # Numeric access should NOT work
        assert 2 not in ym
        assert 3.14 not in ym

        # Values should be accessible by string keys
        assert ym["2"] == "second"
        assert ym["3.14"] == "pi"
        assert ym["4"] == "four_string"
        assert ym["text"] == "regular_value"

    def test_numeric_keys_from_existing_file(self):
        """Test with the numeric_keys.yaml test file."""
        import os
        from pathlib import Path

        test_file = Path(__file__).parent / "data" / "numeric_keys.yaml"

        ym = YAMLConfigManager.from_yaml_file(str(test_file))

        # All keys should be strings
        assert "2" in ym
        assert "3.14" in ym
        assert "4" in ym
        assert "text" in ym

        # Verify correct values
        assert ym["2"] == "second"
        assert ym["3.14"] == "pi"
        assert ym["4"] == "four_string"
        assert ym["text"] == "regular_value"
