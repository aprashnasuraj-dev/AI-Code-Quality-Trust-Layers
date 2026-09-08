import requests


class InventoryClient:
    def __init__(self, inner):
        self._inner = inner

    def fetch(self, sku):
        return self._inner.fetch(sku)

    def reserve(self, sku):
        return self._inner.reserve(sku)


def _unused_helper(value):
    return value.strip()


def parse_manifest(text):
    if not text.startswith("SKU:"):
        raise ValueError("invalid manifest")
    return text[4:]
