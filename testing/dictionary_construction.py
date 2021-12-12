import re
from urllib import parse
import pickle
from testing.scrape_cities import load_city_set


def create_encoded_word_set():
    files_dir = 'C:/Users/Cas/PycharmProjects/WebScraping/OpenTaal-210G-woordenlijsten'
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

    with open('words.p', 'wb') as output_handle:
        pickle.dump(words, output_handle)


def create_frisian_word_set():
    files_dir = 'C:/Users/Cas/PycharmProjects/WebScraping/fy_NL'
    words_file = 'fy_NL.dic'

    words = parse_frisian_words(f'{files_dir}/{words_file}')

    return words


def load_encoded_word_set():
    with open('C:/Users/Cas/PycharmProjects/WebScraping/testing/words.p', 'rb') as input_handle:
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


def create_ngrams(token):
    if len(token) <= 5:
        return {token}

    ngrams = []

    for i in range(5, len(token)):
        matches = re.finditer(f'(?=({"." * i}))', token)

        for match in matches:
            ngrams.append(match.group(1))

    return ngrams


def extract_features(url):
    def update_counts(regex, url_part):
        nonlocal dict_count
        nonlocal city_count

        for token in re.split(regex, url_part):
            ngrams = create_ngrams(token)
            for ngram in ngrams:
                if ngram in word_set:
                    dict_count += 1
                if ngram in city_names:
                    city_count += 1

    split_tokens = re.compile('[&/\\-_\\s]')
    split_hostname_tokens = re.compile('[&/\\-_\\s.]')
    split_query_tokens = re.compile('[&/\\-_?=\\s]')
    split_fragment_tokens = re.compile('[&/\\-_#=\\s]')
    dict_count = 0
    city_count = 0

    word_set = load_encoded_word_set()
    city_names = load_city_set()
    parsed = parse.urlparse(url)

    domain_code = parsed.hostname.split('.')[-1]
    hyphen_count = url.count('-')

    update_counts(split_hostname_tokens, parsed.hostname.lower())
    update_counts(split_tokens, parsed.path.lower())
    update_counts(split_query_tokens, parsed.query.lower())
    update_counts(split_fragment_tokens, parsed.fragment.lower())

    print(f'Words in URL: {dict_count}')
    print(f'Cities in URL: {city_count}')
    print(f'Top level domain code: {domain_code}')
    print(f'Hyphen count: {hyphen_count}')


if __name__ == '__main__':
    extract_features('https://www.doetinchem.nl/contact-en-openingstijden?origin=/contact?#view=bijles&kokosnoten-fryslannen')
    # extract_features('https://www.gemeentedoetinchem.nl/')
    # create_encoded_word_set()
