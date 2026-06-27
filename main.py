import asyncio
import sys

from google.adk.apps import App
from google.adk.runners import InMemoryRunner

from src.workflow import root_agent


async def main() -> None:
    query = (
        " ".join(sys.argv[1:])
        or "Summarize the patient discharge instructions and mention any allergic reactions during the stay."
    )
    app = App(name="agentic_rag_demo", root_agent=root_agent)
    runner = InMemoryRunner(app=app)
    response = await runner.run_debug(query)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
