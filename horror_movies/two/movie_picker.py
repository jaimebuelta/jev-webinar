from ollama import chat
from rich.console import Console
from rich.markdown import Markdown

from movie_search import search as _search
from filter_movies import filter_movie as _filter_movie

console = Console()

# MODEL = 'qwen3.8'     # bigger model, ~32GB RAM
# MODEL = 'qwen3.5:9b'  # smaller model, ~15GB RAM
MODEL = 'qwen3.5:4b'  # even smaller, ~4GB RAM


PROMPT = '''
Recommend me a scary movie from the 80s, checking
that is adequate for my taste.

You can try different years to find the right movie
as well as dig deeper into a particular year.
'''

messages = [{'role': 'user', 'content': PROMPT}]


def search_movie(genre: str, year: int, limit: int):
    '''
    Obtain a list of  movies based on the *genre* and *year*.
    Return up to the number of movies defined in *limit*
    '''
    return _search(genre=genre, year=year, limit=limit)


def verify_movie(movie_info: dict):
    '''
    Validate a movie is adequate to my taste
    '''
    return _filter_movie(movie_info)


available_functions = {
  'search_movie': search_movie,
  'verify_movie': verify_movie,
}

separator = Markdown('---')


while True:

    response = chat(model=MODEL,
                    messages=messages,
                    think=True,
                    tools=[search_movie, verify_movie])
    # Track the context size
    size = round(response.prompt_eval_count / 1000., 3)
    console.print('Current context size: ', size, 'K tokens')

    messages.append(response.message)
    console.print(response.message.thinking, style='dim')
    md_content = Markdown(response.message.content)
    console.print(md_content)

    if response.message.tool_calls:
        for tc in response.message.tool_calls:
            if tc.function.name in available_functions:
                console.print(f"Calling {tc.function.name} with arguments {tc.function.arguments}", style='dim')
                result = available_functions[tc.function.name](**tc.function.arguments)
                console.print(f"Result: {result}", style='dim')
                # add the tool result to the messages
                messages.append({'role': 'tool', 'tool_name': tc.function.name, 'content': str(result)})
    else:
        # end the loop when there are no more tool calls
        break
    # continue the loop with the updated messages
    console.print(separator)
