# Simple movie agent with MCP

An agent that recommends a scary movie from the 80s, checking that it is
adequate for your taste.

- The movies come from an [MCP](https://modelcontextprotocol.io) server
  (`mcp_server/`) with a catalogue of horror movies (1970-2000). The agent can
  search them by year, synopsis or cast and crew.
- Each candidate is checked with a decision model (`verify_movie.py`): not
  too much gore, and scary but not too scary.

There are two versions of the agent:

| Script | What it does |
|--------|--------------|
| `agent.py` | Hand-written tool-calling loop using a local model in [Ollama](https://ollama.com), connected to the MCP server. |
| `agent_openai.py` | The same agent using the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/), which runs the loop for you. |

## Prerequisites

- [uv](https://docs.astral.sh/uv/) to manage Python and the dependencies.
- [Ollama](https://ollama.com/download) installed and running, to use
  `agent.py` or the `ollama` decision engine.
- At least one key for the decision model, depending on the engine you use
  (see below):
  - A TypeSafe API key from https://typesafe.ai, for `jev` (the default).
  - An OpenAI API key from https://platform.openai.com, for `openai`. It is
    also required to run `agent_openai.py`.
- Enough RAM for the local model. The default `qwen3.5:4b` needs around 4GB.

## Download the Ollama models

Pull the model for the agent:

```bash
ollama pull qwen3.5:4b
```

If you have more memory, you can use a bigger model, changing `MODEL` in
`agent.py` and pulling the image. For example:

```bash
ollama pull qwen3.5:9b  # ~15GB RAM
```

If you want to use Ollama as the decision model (`FILTER_ENGINE=ollama`), pull
the model as well:

```bash
ollama pull tev1
```
Look at the code in verify_movie.py for other alternatives. Remember to pull them
before running the code

Check that the models are available with `ollama list`.

## Configuration

Copy `.env.template` to `.env` and fill it with your values:

```bash
cp .env.template .env
```

- `TYPESAFE_API_KEY`: your TypeSafe key, for the `jev` engine.
- `OPENAI_API_KEY`: your OpenAI key, for the `openai` engine and
  `agent_openai.py`.
- `FILTER_ENGINE`: the decision model used to verify the movies, one of `jev`,
  `ollama` or `openai`. Defaults to `jev`.

You can check the decision model on its own with two example movies:

```bash
uv run verify_movie.py
```

## Running it

The agents need the MCP server running. In one terminal, start it from
`mcp_server/` (it has its own environment):

```bash
cd mcp_server
uv venv
uv pip install -r requirements.txt
uv run server.py
```

The server listens on `http://127.0.0.1:8000/mcp`. See
[`mcp_server/README.md`](mcp_server/README.md) for the details.

In another terminal, install the dependencies of the agent and run it:

```bash
uv venv
uv pip install -r requirements.txt
uv run agent.py
```

Or, to use the OpenAI version:

```bash
uv run agent_openai.py
```

Enjoy!
