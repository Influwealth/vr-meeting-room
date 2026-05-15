class PresenterAgent:
    def __init__(self):
        self.name = "presenter_agent"

    async def summarize_slide(self, slide_text: str) -> str:
        return f"summary_placeholder:{slide_text[:64]}"

