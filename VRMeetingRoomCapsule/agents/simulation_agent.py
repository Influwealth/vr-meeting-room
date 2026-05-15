class SimulationAgent:
    def __init__(self):
        self.name = "simulation_agent"

    async def run(self, capsule_id: str, params: dict) -> dict:
        return {"capsule_id": capsule_id, "result": "simulation_placeholder", "params": params}

