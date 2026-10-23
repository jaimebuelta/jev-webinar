# Movies MCP server

An [MCP](https://modelcontextprotocol.io) server that exposes a catalogue of
horror movies (1970-2000, ~1,550 movies from TMDB) over **Streamable HTTP**.

## Running it

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv venv
uv pip install -r requirements.txt
uv run server.py
```

The MCP endpoint is served at `http://127.0.0.1:8000/mcp`. The host and port
can be changed with the `HOST` and `PORT` environment variables, and the data
file with `MOVIES_FILE`.

To connect from Claude Code:

```bash
claude mcp add --transport http movies http://127.0.0.1:8000/mcp
```

You can also explore it with the MCP Inspector
(`npx @modelcontextprotocol/inspector`), selecting the "Streamable HTTP"
transport and the URL above.

## Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `movies_by_year` | `year`, `max_results=50` | Movies released in a given year, most voted first. |
| `search_synopsis` | `text`, `max_results=20` | Movies whose overview or tagline contains all the words in `text` (case insensitive). |
| `search_crew` | `name`, `role=None`, `max_results=20` | Movies with a cast or crew member whose name contains `name`. `role` restricts it to `"cast"` or a crew job like `"Director"`, `"Screenplay"` or `"Original Music Composer"`. Without `role`, all cast and crew fields are searched. |
| `list_crew_roles` | | Lists the roles accepted by `search_crew`. |

Results are capped at 50 movies and include the `total` number of matches. Each
movie is returned as a summary: title, year, release date, genres, overview,
director, top-billed cast and votes. `search_crew` also returns which
people/roles matched.

## Data

- `movies.json` — the data the server uses: a list of movies, each with
  `id`, `title`, `original_title`, `year`, `release_date`, `genres`,
  `overview`, `tagline`, `runtime`, `original_language`, `vote_average`,
  `vote_count`, `imdb_id`, `cast` (top 20, `name` + `character`) and `crew`
  (a mapping of job to names, e.g. `{"Director": ["John Carpenter"]}`).
- `movies_raw.json` — the original dump of TMDB API responses.
- `prepare_movies.py` — regenerates `movies.json` from the raw dump:

  ```bash
  uv run prepare_movies.py movies_raw.json movies.json
  ```

The data is loaded at startup, so restart the server after changing
`movies.json`.
