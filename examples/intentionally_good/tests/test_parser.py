import pytest

from goodpkg.parser import parse_invoice_rows


def test_parse_invoice_rows_rejects_malformed_empty_input():
    with pytest.raises(ValueError):
        parse_invoice_rows("")
