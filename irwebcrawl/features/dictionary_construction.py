import pickle
import re
from urllib import parse
import os


def create_encoded_word_set():
    files_dir = '/OpenTaal-210G-woordenlijsten'
    gekeurd = 'OpenTaal-210G-basis-gekeurd.txt'
    ongekeurd = 'OpenTaal-210G-basis-ongekeurd.txt'
    flexievormen = 'OpenTaal-210G-flexievormen.txt'
    verwarrend = 'OpenTaal-210G-verwarrend.txt'

    words = set()

    words.update(parse_words(f'{files_dir}/{gekeurd}'))
    words.update(parse_words(f'{files_dir}/{ongekeurd}'))
    words.update(parse_words(f'{files_dir}/{flexievormen}'))
    words.update(parse_words(f'{files_dir}/{verwarrend}'))
    words.update(create_frisian_word_set())
    words.remove('')

    words = {word for word in words if len(word) > 1}
    to_delete = set()
    for word in words:
        if re.fullmatch('[0-9]+', word):
            to_delete.add(word)
    words.difference_update(to_delete)
    words.remove('www')

    root_dir = os.path.abspath(os.path.dirname(__file__))
    words_path = os.path.join(root_dir, '../pickles/words.p')

    with open(words_path, 'wb') as output_handle:
        pickle.dump(words, output_handle)


def create_frisian_word_set():
    files_dir = '/fy_NL'
    words_file = 'fy_NL.dic'

    words = parse_frisian_words(f'{files_dir}/{words_file}')

    return words


def load_encoded_word_set():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    words_path = os.path.join(root_dir, '../pickles/words.p')

    with open(words_path, 'rb') as input_handle:
        words = pickle.load(input_handle)

    return words


def parse_words(filename):
    split_tokens = re.compile('[/\\-_\\s]')
    words = set()

    with open(filename, 'r', encoding='utf-8') as input_handle:
        for line in input_handle:
            for part in re.split(split_tokens, line.rstrip().lower()):
                words.add(parse.quote(part))

    return words


def parse_frisian_words(filename):
    split_tokens = re.compile('[/\\-_\\s]')
    words = set()

    with open(filename, 'r') as input_handle:
        next(input_handle)
        for line in input_handle:
            for part in re.split(split_tokens, line.rstrip().lower().split('/')[0]):
                words.add(parse.quote(part))

    return words


if __name__ == '__main__':
    create_encoded_word_set()
