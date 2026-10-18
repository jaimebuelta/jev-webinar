from pathlib import Path
import argparse
from PIL import Image as PILImage, ImageDraw

from typesafe_sdk import Image, TypeSafeClient

from dotenv import load_dotenv
load_dotenv()


QUESTIONS = {
    'animal_presence': {
        'type': 'noul',
        'instructions': 'Is there an animal in the image?',
        'criteria': {
            'true': 'There is an animal',
            'false': 'No animal',
        },
    },
    'what_animal': {
        'type': 'choice',
        'instructions': 'What animal is in the image?',
        'criteria': {
            'lion': 'A lion',
            'tiger': 'A tiger',
            'dog': 'A dog',
            'cat': 'A cat',
            'other': 'Other animal',
            'none': 'No animals',
        }
    },
}


def main(filename, box, scifi):
    questions = QUESTIONS
    if box:
        QUESTIONS['bounding_box'] = {'type': 'box', 'instructions': 'the animal in `image`'}

    if scifi:
        questions = {
            'what_scifi': {
                'type': 'choice',
                'instructions': 'What scifi franchise is this image from?',
                'criteria': {
                    'startrek': 'Star Trek',
                    'starwars': 'Star Wars',
                    'other': 'Other or no scifi',
                }
            }
        }

    with TypeSafeClient() as client:
        result = client.system_one(
            model="jev-preview",  # Important to be able to show the box
            state={"image": Image(Path(filename))},
            questions=questions,
            extra_headers={"TypeSafe-Danger-Zone-Images": "true"},
        )
        print(result.answers)

    if box:
        animal = result.answers['bounding_box']
        edges = animal.box
        draw_box(filename, edges)


def draw_box(filename, edges):
    image = PILImage.open(filename)
    width, height = image.size
    box = (
        round(edges.left * width),
        round(edges.top * height),
        round(edges.right * width),
        round(edges.bottom * height),
    )
    draw = ImageDraw.Draw(image)
    draw.rectangle(box, outline="red", width=5)
    image.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('--box', action='store_true', default=False)
    parser.add_argument('--scifi', action='store_true', default=False)

    args = parser.parse_args()

    if args.box and args.scifi:
        print('Sorry, only either box or scifi at the time')

    main(args.filename, args.box, args.scifi)
