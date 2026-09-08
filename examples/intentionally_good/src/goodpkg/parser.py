"""Small input parser with explicit test evidence."""


def parse_invoice_rows(text: str) -> list[str]:
    if not text.strip():
        raise ValueError("invoice input must not be empty")
    return [row.strip() for row in text.splitlines() if row.strip()]
