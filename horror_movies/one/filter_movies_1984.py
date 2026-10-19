import json
from typesafe_sdk import TypeSafeClient
from rich.console import Console

from dotenv import load_dotenv
load_dotenv()

FILENAME = 'one/horror_movies_1984.json'

console = Console()

MODEL = "jev-latest"

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
    'subgenre': {
        'type': 'choice',
        'instructions': 'Subgenres of horror movies',
        'criteria': {
            'slasher': 'A masked or unstoppable killer picks off a group one by one, usually ending with a lone survivor',
            'haunted house': 'Restless spirits tied to a place, with dread built from creaks, cold spots and things '
                             'glimpsed at the edge of the frame.',
            'psychological': 'Fear comes from the mind: paranoia, unreliable perception and characters unravelling',
            'supernatural': 'supernatural creatures like vampires, werewolves, etc',
            'comedy': 'cares and laughs in the same breath, from slapstick gore to deadpan parody',
            'survival': 'Outsiders stranded in hostile territory, hunted by locals or simply trying to get out alive.',
            'other': 'Other types',
        }
    }
}


def filter_movie(movie_info):
    '''
    Return whether the movie is adequate for my taste or not, and its subgenre
    '''
    with TypeSafeClient() as client:
        result = client.system_one(state={"movie": movie_info},
                                   questions=QUESTIONS, model=MODEL)

    subgenre = result.answers['subgenre'].choice

    if result.answers['gore'].noul > 0.80:
        result = 'The movie is not adequate (too much gore)'
        adequate = False
    else:
        scary = result.answers['scary']
        key, probability = max(scary.probabilities.items(), key=lambda x: x[1])
        name = scary.legend[key]
        if name == 'Not too scary':
            result = 'The movie is adequate'
            adequate = True
        else:
            result = 'The movie is not adequate, either too scary or not scary at all'
            adequate = False

    return {'adequate': adequate, 'result': result, 'subgenre': subgenre}


def main():

    with open(FILENAME) as fp:
        movies = json.load(fp)

    for movie in movies:
        result = filter_movie(movie)
        if result['adequate']:
            style = 'green'
        else:
            style = 'red'
        info = result['result']
        subgenre = result['subgenre']
        console.print(f'[{style}]{movie["title"]}[/{style}] ({subgenre}): {info}')


if __name__ == '__main__':
    main()
