class LangAgent:
    def __init__(self, translation_client=None, catalog_client=None):
        self.translation = translation_client
        self.catalog = catalog_client

    async def explain_product(self, product_id: str, lang_code: str) -> str:
        base_text = f"product_description_en_placeholder:{product_id}"
        if self.translation is None:
            return base_text
        return await self.translation.translate(text=base_text, from_="en", to=lang_code)

