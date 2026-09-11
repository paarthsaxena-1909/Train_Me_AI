# Evaluation graph in LangGraph Studio

This folder contains the local LangGraph Studio configuration for the
evaluation graph used by the FastAPI evaluation-avatar prototype.

The configured graph is the existing
`backend/app/services/evaluations/evaluation_graph.py:evaluation_graph`.
No application graph code is duplicated here.

## What Studio provides

Studio can render the graph, run it with JSON input, and show the state updates
produced by each node. It is useful for interactive development and debugging;
the repository's automated tests remain the source of regression coverage.

This graph uses Graph mode rather than Chat mode because its state is a typed
`message`/`response_text` mapping, not LangGraph `MessagesState`.

## Prerequisites

- Python 3.11 or newer
- Dependencies from `backend/requirements.txt`
- The LangGraph CLI with its in-memory development server
- A LangSmith account and API key for connecting Studio to the local server

Install the Python dependencies from the backend directory:

```bash
cd backend
python -m pip install -r requirements.txt
python -m pip install -U "langgraph-cli[inmem]"
```

If you use a virtual environment, activate it before running these commands.

## Environment

The config loads environment variables from `backend/app/.env`. Add a
LangSmith key there if it is not already present:

```dotenv
LANGSMITH_API_KEY=lsv2-your-key
```

Do not commit that file or paste the key into this README. The graph itself
uses fixed local mock responses and does not need an LLM provider key. To keep
local runs from sending traces to LangSmith, add:

```dotenv
LANGSMITH_TRACING=false
```

When tracing is disabled, Studio can still connect to the local server, but
LangSmith trace and dataset features will not be available.

## Start Studio

Run the development server from this folder so it picks up the local config:

```bash
cd backend/langgraph-studio
langgraph dev --no-browser
```

The CLI prints a Studio URL similar to:

```text
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

Open that URL, select the `evaluation` graph, and use Graph mode to run it.
If the browser cannot reach localhost, restart with `--tunnel`:

```bash
langgraph dev --no-browser --tunnel
```

## Example Studio input

Submit this JSON in the graph input panel:

```json
{
  "message": "How should I greet a customer?"
}
```

The graph executes:

```text
START -> generate_response -> END
```

The output contains one of the fixed prototype responses:

```json
{
  "message": "How should I greet a customer?",
  "response_text": "..."
}
```

## Automated verification

From the backend directory, run the focused evaluation tests:

```bash
cd backend
pytest -q app/test/test_evaluations.py
```

The test suite requires the backend dependencies to be installed first.

To validate the graph directly without Studio:

```bash
cd backend
PYTHONPATH=. python -c \
  'from app.services.evaluations.evaluation_graph import evaluation_graph; print(evaluation_graph.invoke({"message": "Hello"}))'
```

## Configuration reference

- [LangSmith Studio](https://docs.langchain.com/oss/python/langgraph/studio)
- [Run a local LangGraph server](https://docs.langchain.com/oss/python/langgraph/local-server)
- [Studio workflows](https://docs.langchain.com/langsmith/use-studio)
