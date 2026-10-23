"""MCP server exposing a horror movie catalogue over Streamable HTTP.

    uv venv
    uv pip install -r requirements.txt
    uv run server.py

The MCP endpoint is served at http://127.0.0.1:8000/mcp
"""

import json
import os
from pathlib import Path

from mcp.server.mcpserver import MCPServer

MOVIES_FILE = Path(os.environ.get("MOVIES_FILE", Path(__file__).parent / "movies.json"))
MAX_RESULTS = 50

mcp = MCPServer(
    "movies",
    instructions=(
        "Catalogue of horror movies. Search them by release year, by text in "
        "the synopsis, or by cast and crew members (director, writer, etc.)."
    ),
)


def load_movies():
    with open(MOVIES_FILE) as f:
        return json.load(f)


MOVIES = load_movies()


def summary(movie):
    """Compact representation of a movie returned by the tools."""
    return {
        "id": movie["id"],
        "title": movie["title"],
        "year": movie["year"],
        "release_date": movie["release_date"],
        "genres": movie["genres"],
        "overview": movie["overview"],
        "director": movie["crew"].get("Director", []),
        "cast": [c["name"] for c in movie["cast"][:5]],
        "vote_average": movie["vote_average"],
        "vote_count": movie["vote_count"],
    }


def limit(results, max_results):
    max_results = max(1, min(max_results, MAX_RESULTS))
    return {
        "total": len(results),
        "returned": min(len(results), max_results),
        "movies": results[:max_results],
    }


@mcp.tool()
def movies_by_year(year: int, max_results: int = 50) -> dict:
    """Get the movies released in a given year (e.g. 1980), most voted first."""
    results = [m for m in MOVIES if m["year"] == year]
    results.sort(key=lambda m: m["vote_count"] or 0, reverse=True)
    return limit([summary(m) for m in results], max_results)


@mcp.tool()
def search_synopsis(text: str, max_results: int = 20) -> dict:
    """Search movies whose synopsis (overview or tagline) contains the given text.

    The search is case insensitive. Several words separated by spaces must all
    appear in the synopsis, in any order.
    """
    words = text.lower().split()
    results = []
    for movie in MOVIES:
        synopsis = f"{movie['overview']} {movie['tagline']}".lower()
        if all(word in synopsis for word in words):
            results.append(summary(movie))
    return limit(results, max_results)


@mcp.tool()
def search_crew(name: str, role: str | None = None, max_results: int = 20) -> dict:
    """Search movies by a person in the cast or crew.

    `name` is matched case insensitively as a substring (e.g. "carpenter").
    `role` optionally restricts the search to one role (case insensitive):
    "cast" for actors, or a crew job such as
    "director", "writer", "screenplay", "producer", "original music composer",
    "director of photography", "editor"... Use `list_crew_roles` to see them.
    Without `role`, every cast and crew field is searched.
    """
    name = name.lower()
    role = role.lower().strip() if role else None
    results = []
    for movie in MOVIES:
        matches = []
        if role is None or role in ("cast", "actor", "actress"):
            for c in movie["cast"]:
                if name in c["name"].lower():
                    matches.append(f"{c['name']} (cast, as {c['character']})")
        if role not in ("cast", "actor", "actress"):
            for job, people in movie["crew"].items():
                if role is not None and role != job.lower():
                    continue
                for person in people:
                    if name in person.lower():
                        matches.append(f"{person} ({job})")
        if matches:
            results.append({**summary(movie), "matches": matches})
    return limit(results, max_results)


@mcp.tool()
def list_crew_roles() -> list[str]:
    """List the available crew roles (jobs) that can be used in `search_crew`."""
    roles = {"Cast"}
    for movie in MOVIES:
        roles.update(movie["crew"])
    return sorted(roles)


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8000")),
    )
