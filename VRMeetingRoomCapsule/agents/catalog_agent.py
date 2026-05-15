class CatalogAgent:
    def __init__(self):
        self.name = "catalog_agent"

    async def explain(self, product_id: str, lang_code: str) -> str:
        return f"catalog_placeholder:{product_id}:{lang_code}"

