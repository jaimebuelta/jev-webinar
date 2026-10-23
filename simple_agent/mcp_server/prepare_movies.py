"""Convert the raw TMDB API dump (movies_raw.json) into a clean movies.json.

The raw file is a cache of TMDB responses keyed by request path. This script
keeps only the movie detail responses and flattens them into a list of movies
with the fields the MCP server needs.

    uv run prepare_movies.py [movies_raw.json] [movies.json]
"""

import json
import sys

MAX_CAST = 20


def convert_movie(raw):
    credits = raw.get("credits", {})
    crew = {}
    for member in credits.get("crew", []):
        names = crew.setdefault(member["job"], [])
        if member["name"] not in names:
            names.append(member["name"])

    cast = sorted(credits.get("cast", []), key=lambda c: c.get("order", 0))
    release_date = raw.get("release_date") or ""
    return {
        "id": raw["id"],
        "title": raw["title"],
        "original_title": raw.get("original_title"),
        "year": int(release_date[:4]) if release_date[:4].isdigit() else None,
        "release_date": release_date,
        "genres": [g["name"] for g in raw.get("genres", [])],
        "overview": raw.get("overview", ""),
        "tagline": raw.get("tagline", ""),
        "runtime": raw.get("runtime"),
        "original_language": raw.get("original_language"),
        "vote_average": raw.get("vote_average"),
        "vote_count": raw.get("vote_count"),
        "imdb_id": raw.get("imdb_id"),
        "cast": [
            {"name": c["name"], "character": c.get("character", "")}
            for c in cast[:MAX_CAST]
        ],
        "crew": crew,
    }


def main(src="movies_raw.json", dst="movies.json"):
    with open(src) as f:
        raw = json.load(f)

    movies = [
        convert_movie(value)
        for key, value in raw.items()
        if key.startswith("/movie/") and "title" in value
    ]
    movies.sort(key=lambda m: (m["year"] or 0, m["title"]))

    with open(dst, "w") as f:
        json.dump(movies, f, indent=1, ensure_ascii=False)
    print(f"Wrote {len(movies)} movies to {dst}")


if __name__ == "__main__":
    main(*sys.argv[1:])
