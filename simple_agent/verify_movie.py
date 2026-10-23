import time
from typesafe_sdk import TypeSafeClient
import ollama
import os

from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

MODEL = "jev-latest"
# OLLAMA_MODEL = 'clef'  # bigger
# OLLAMA_MODEL = 'clef-flash'
# OLLAMA_MODEL = 'nimble'
OLLAMA_MODEL = 'tev1'  # smallest

QUESTIONS = {
    'scary': {
        'type': 'score',
        'instructions': 'How scary is this movie?',
        'criteria': ['No scary', 'Not too scary', 'Very scary'],
    },
    'gore': {
        'type': 'noul',
        'instructions': 'Is there  a big amount of gore in this movie?',
        'criteria': {
            'true': 'There is a lot of gore in the movie',
            'false': 'No gore in the movie',
        }
    },
}

QUESTIONS_OPENAI = [
    {
        'name': 'scary',
        'type': 'score',
        'instructions': 'How scary is this movie?',
        'levels': [
            {
                'label': 'No scary',
                'description': 'The movie is not really scary',
            },
            {
                'label': 'Not too scary',
                'description': 'The movie has tension, but overall is not terrifying',
            },
            {

                'label': 'Very scary',
                'description': 'The movie is based on terror and generaly quite terrorific',
            }

        ]
    },
    {
        'type': 'predicate',
        'name': 'gore',
        'instructions': 'Is there a big amount of gore in this movie?',
    },
]


def measure(func):

    def measurement(*args):
        before = time.perf_counter_ns()
        result = func(*args)
        after = time.perf_counter_ns()
        total_ns = after - before
        print(f'Total call time {total_ns // 1_000_000} ms')
        return result

    return measurement


@measure
def filter_movie_jev(movie_info):
    with TypeSafeClient() as client:
        result = client.system_one(state={"movie": movie_info},
                                   questions=QUESTIONS, model=MODEL)

    if result.answers['gore'].noul > 0.80:
        return 'The movie is not adequate (too much gore)'

    scary = result.answers['scary']
    key, probability = max(scary.probabilities.items(), key=lambda x: x[1])
    name = scary.legend[key]
    if name == 'Not too scary':
        return 'The movie is adequate'

    return 'The movie is not adequate, either too scary or not scary at all'


@measure
def filter_movie_ollama(movie_info):
    result = ollama.systemone(model=OLLAMA_MODEL,
                              state={'movie': movie_info}, questions=QUESTIONS)

    if result.answers['gore'].noul > 0.80:
        return 'The movie is not adequate (too much gore)'

    scary = result.answers['scary']
    key, probability = max(scary.probabilities.items(), key=lambda x: x[1])
    name = scary.legend[key]
    if name == 'Not too scary':
        return 'The movie is adequate'

    return 'The movie is not adequate, either too scary or not scary at all'


@measure
def filter_movie_openai(movie_info):

    client = OpenAI()

    decision = client.decisions.create(model="gpt-6-luna", input=str(movie_info),
                                       questions=QUESTIONS_OPENAI)

    if decision.answers[1].probability > 0.80:
        return 'The movie is not adequate (too much gore)'

    scary = decision.answers[0]
    top_score = max(scary.probabilities, key=lambda x: x.probability)
    name = top_score.label
    if name == 'Not too scary':
        return 'The movie is adequate'

    return 'The movie is not adequate, either too scary or not scary at all'


def verify_movie(movie_info):

    engine = os.environ.get('FILTER_ENGINE', 'jev')

    if engine.lower() == 'ollama':
        return filter_movie_ollama(movie_info)
    elif engine.lower() == 'openai':
        return filter_movie_openai(movie_info)
    elif engine.lower() == 'jev':
        return filter_movie_jev(movie_info)

    return filter_movie_jev(movie_info)



# PREPARE A COUPLE OF EXAMPLE MOVIES TO TEST THE FUNCTIONALITY
NOT_ADEQUATE_MOVIE = {
    'title': 'The Day of the Beast',
    'overview': 'When a rogue priest discovers the exact date the Antichrist will be born, he enlists a Death Metal record store clerk and a cheesy TV psychic for an urban spree of gore, sacrilege and twisted humor to prevent the Apocalypse.'
}

ADEQUATE_MOVIE = {
    'title': 'Gremlins',
    'overview': 'After receiving an exotic small animal as a Christmas gift, a young man inadvertently breaks three important rules concerning his new pet, which unleashes a horde of malevolently mischievous creatures on a small town.'
}


if __name__ == '__main__':
    for movie in (ADEQUATE_MOVIE, NOT_ADEQUATE_MOVIE):
        result = verify_movie(movie)
        print(f'Movie {movie["title"]} is {result}')
