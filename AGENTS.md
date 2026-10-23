# AGENTS.md

Guidance for AI coding agents working in this repository.

## What this is

Workshop material showing how to build agents, using Ollama (local models)
or OpenAI. It also shows how to use Jev, TypeSafe's decision model (via
`typesafe-sdk`), both on its own and inside agents.

The audience reads this code, so **clarity beats cleverness**. Code
should be short, linear and easy to explain on a slide or screen share.

## Layout

Each top-level directory is an independent exercise with its own
`requirements.txt`, `.env.template` and `README.md`. There is no shared
package and no root-level environment.

| Directory | What it shows |
|-----------|---------------|
| `horror_movies/one/` | Simplest Jev call: filter a JSON list of 1984 horror movies (`score`, `noul`, `choice` questions). |
| `horror_movies/two/` | Hand-written Ollama tool-calling loop (`movie_picker.py`) using TMDB search (`movie_search.py`) and a pluggable decision engine (`filter_movies.py`). |
| `image/` | Jev on images: animal detection, `--box` bounding box, `--scifi` classification. |
| `simple_agent/` | Same movie agent, tools served by an MCP server. `agent.py` = manual Ollama loop + MCP client; `agent_openai.py` = OpenAI Agents SDK + MCP; `verify_movie.py` = decision engine. |
| `simple_agent/mcp_server/` | Streamable HTTP MCP server over `movies.json`, with its own `requirements.txt`. Start it before running the agents. |

`horror_movies/` is the exception to "one dir, one env": `one/` and `two/`
share `horror_movies/requirements.txt` and `.env`, and scripts are run from
`horror_movies/` (e.g. `uv run one/filter_movies_1984.py`) because paths like
`FILENAME = 'one/...'` are relative to it.

## Tooling

- Python, managed with **uv**:
  ```bash
  uv venv
  uv pip install -r requirements.txt
  uv run <script>.py
  ```
- Dependencies live in plain, unpinned `requirements.txt` files (no
  `pyproject.toml`). Keep that style.
- Configuration comes from a `.env` file loaded with `python-dotenv`
  (`load_dotenv()` at import time). Every new variable must be added to that
  directory's `.env.template` with a `<placeholder>` value.
- There are no tests, linters or CI. Verify changes by running the script.
  Most scripts call paid/remote APIs (TypeSafe, OpenAI, TMDB) or need Ollama
  running locally, so ask before running anything that costs money.

## Code conventions

Match the existing scripts:

- **Flat scripts**, not packages or classes: module-level constants, a few
  functions, then `main()` under `if __name__ == '__main__':`. Agent loops
  run at module level instead, either directly (`movie_picker.py`) or via
  `asyncio.run(main())` (`simple_agent/`).
- **Constants in UPPER_CASE at the top**: `MODEL`, `QUESTIONS`, `PROMPT`,
  `MCP_URL`, file names. Model choices are listed as commented-out
  alternatives with a size/cost note, the active one last:
  ```python
  # MODEL = 'qwen3.5:9b'  # smaller model, ~15GB RAM
  MODEL = 'qwen3.5:4b'  # even smaller, ~4GB RAM
  ```
- **Jev questions** are dicts keyed by name with `type` (`score`, `noul`,
  `choice`, `box`), `instructions` and `criteria` (`box` has no `criteria`).
  The OpenAI engine uses a different shape (`QUESTIONS_OPENAI`): a list of
  dicts with `name`, `type` (`score`, `predicate`) and `levels`. Call Jev through
  `with TypeSafeClient() as client: client.system_one(state=..., questions=..., model=MODEL)`.
  Default model is `"jev-latest"`; `"jev-preview"` is needed for images/boxes.
- **Pluggable decision engine**: the `FILTER_ENGINE` env var (`jev` |
  `ollama` | `openai`) selects `filter_movie_jev/_ollama/_openai`, falling
  back to Jev. The entry point is `filter_movie()` in `horror_movies/two/`
  and `verify_movie()` in `simple_agent/`. Timings are printed with the
  `@measure` decorator.
- **Tools for agents** are thin wrappers with a short docstring (the docstring
  is what the LLM sees). Real implementations are imported with a leading
  underscore alias: `from verify_movie import verify_movie as _verify_movie`.
- **Output with `rich`**: `Console()`, `Markdown(...)` for model responses,
  `style='dim'` for thinking, tool calls and results, and `Markdown('---')`
  separators between turns. Print the context size in hand-written Ollama
  loops.
- **Docstrings** are short. Workshop scripts use `'''` and single quotes.
  Helper scripts (`movie_search.py`, `mcp_server/`) use `"""`, double quotes
  and a module docstring with usage examples. Follow the file you are editing.
- Short inline comments explain *why* or narrate a step for the audience
  (`# end the loop when there are no more tool calls`). Keep them.
- Prefer the standard library over extra dependencies when it is easy (e.g.
  `urllib.request` in `movie_search.py`).
- **Deliberate duplication**: `simple_agent/verify_movie.py` mirrors
  `horror_movies/two/filter_movies.py` so each exercise stands alone. Don't
  factor them into a shared module; if you fix one, consider fixing the other.
- **Follow PEP 8**, but lines may run past 79 characters when that reads
  better (stay under ~120).

## Docs

Each exercise has a `README.md` with: what it does, how to get keys/models
(`ollama pull ...`), the `uv` commands to install and run, and a friendly
sign-off ("Enjoy!", "Have fun!"). Update it when you change how an exercise
is run or configured.

## Secrets and data

- Never commit `.env` files (gitignored) or print their values.
- Data files are committed with the exercises: `horror_movies_1984.json` and
  `mcp_server/movies.json`. The latter is generated from `movies_raw.json` with
  `prepare_movies.py`; regenerate it rather than editing it by hand.
- `.movie_cache.json` (TMDB response cache) is local only and gitignored.

## Git

- Work on `main`; commit messages are short, imperative, sentence case
  (e.g. "Add READMEs", "Add the image example").
- Only commit or push when asked.
