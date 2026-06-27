clean: # clean dependencies and coverage report
	@echo ">> cleaning files"
	@rm -rf .venv .ruff_cache .langgraph_api __pycache__


install: # install dependencies in the devcontainer
	@echo ">> installing dependencies"
	@poetry lock
	@poetry install


dev: # start ADK web UI with graph visualizer and chat interface (localhost:8000)
	poetry run adk web

run: # run the agent interactively in the terminal
	poetry run adk run

api: # start ADK REST API server for programmatic testing
	poetry run adk api_server

eval: # run evaluation sets against the agent
	poetry run adk eval src/ evals/