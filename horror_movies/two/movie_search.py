#!/usr/bin/env python3
"""Search movies by genre, year and performers; show title, synopsis and main crew.

IMDb has no free public search API, so this uses TMDB (The Movie Database),
which exposes the same data (including each movie's IMDb id).
Get a free API key at https://www.themoviedb.org/settings/api and put it in a
.env file (or export it):

    TMDB_API_KEY=your_key

Examples:
    ./movie_search.py --genre horror --year 1980
    ./movie_search.py --genre horror --performer "Jamie Lee Curtis" --limit 3
    ./movie_search.py --performer "Vincent Price" --performer "Peter Lorre" --json
    ./movie_search.py --clear-cache

API responses are cached forever in .movie_cache.json next to this script, so
repeating a query gives the same result without hitting the network.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # finds .env in this script's directory or a parent; shell vars win

BASE = "https://api.themoviedb.org/3"
CACHE_FILE = Path(__file__).with_name(".movie_cache.json")
_cache = None
RETRIES = 3
CREW_JOBS = {
    "Director": "Director",
    "Screenplay": "Writer",
    "Writer": "Writer",
    "Novel": "Writer",
    "Original Music Composer": "Composer",
    "Director of Photography": "Cinematographer",
    "Producer": "Producer",
}


def load_cache():
    global _cache
    if _cache is None:
        try:
            _cache = json.loads(CACHE_FILE.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            _cache = {}
    return _cache


def clear_cache():
    CACHE_FILE.unlink(missing_ok=True)


def api(path, **params):
    # key excludes the API key so the cache survives key changes
    cache_key = f"{path}?{urllib.parse.urlencode(sorted(params.items()))}"
    cache = load_cache()
    if cache_key in cache:
        return cache[cache_key]

    key = os.environ.get("TMDB_API_KEY")
    if not key:
        sys.exit("Error: set the TMDB_API_KEY environment variable.")
    params["api_key"] = key
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    for attempt in range(1, RETRIES + 1):
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                data = json.load(resp)
            break
        except urllib.error.HTTPError as e:
            sys.exit(f"API error {e.code}: {e.read().decode(errors='replace')}")
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == RETRIES:
                sys.exit(f"Network error: {getattr(e, 'reason', e)}")
            time.sleep(attempt)  # transient network issue, back off and retry

    cache[cache_key] = data
    tmp = CACHE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(cache, ensure_ascii=False))
    tmp.replace(CACHE_FILE)  # atomic, so an interrupted run can't corrupt it
    return data


def genre_id(name):
    genres = api("/genre/movie/list")["genres"]
    for g in genres:
        if g["name"].lower() == name.lower():
            return g["id"]
    sys.exit("Unknown genre. Valid: " + ", ".join(sorted(g["name"] for g in genres)))


def person_id(name):
    results = api("/search/person", query=name)["results"]
    if not results:
        sys.exit(f"Performer not found: {name}")
    return results[0]["id"]


def search(genre=None, year=None, performers=(), limit=5):
    print(f'Searching {genre}, {year}')
    params = {"sort_by": "popularity.desc"}
    if genre:
        params["with_genres"] = genre_id(genre)
    if year:
        params["primary_release_year"] = year
    if performers:
        # comma = AND: movies featuring all the given performers
        params["with_cast"] = ",".join(str(person_id(p)) for p in performers)
    return api("/discover/movie", **params)["results"][:limit]


def details(movie_id):
    m = api(f"/movie/{movie_id}", append_to_response="credits")
    crew = {}
    for c in m["credits"]["crew"]:
        role = CREW_JOBS.get(c["job"])
        if role and c["name"] not in crew.setdefault(role, []):
            crew[role].append(c["name"])
    return {
        "title": m["title"],
        "year": (m.get("release_date") or "")[:4],
        "imdb_id": m.get("imdb_id"),
        "genres": [g["name"] for g in m["genres"]],
        "synopsis": m.get("overview", ""),
        "crew": crew,
        "cast": [c["name"] for c in m["credits"]["cast"][:5]],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--genre", help="e.g. Horror, Comedy, Drama")
    p.add_argument("--year", type=int, help="release year")
    p.add_argument("--performer", action="append", default=[],
                   help="actor name; repeat to require several")
    p.add_argument("--limit", type=int, default=5, help="max movies (default 5)")
    p.add_argument("--json", action="store_true", help="output JSON")
    p.add_argument("--clear-cache", action="store_true",
                   help="delete the local cache before searching")
    a = p.parse_args()
    if a.clear_cache:
        clear_cache()
        if not (a.genre or a.year or a.performer):
            print("Cache cleared.")
            return
    if not (a.genre or a.year or a.performer):
        p.error("give at least one of --genre, --year, --performer")

    movies = [details(m["id"]) for m in search(a.genre, a.year, a.performer, a.limit)]
    if a.json:
        print(json.dumps(movies, indent=2, ensure_ascii=False))
        return
    if not movies:
        print("No movies found.")
    for m in movies:
        print(f"{m['title']} ({m['year']})  [{', '.join(m['genres'])}]")
        if m["imdb_id"]:
            print(f"  https://www.imdb.com/title/{m['imdb_id']}/")
        print(f"  Synopsis: {m['synopsis']}")
        for role, names in m["crew"].items():
            print(f"  {role}: {', '.join(names[:3])}")
        print(f"  Cast: {', '.join(m['cast'])}\n")


if __name__ == "__main__":
    main()
