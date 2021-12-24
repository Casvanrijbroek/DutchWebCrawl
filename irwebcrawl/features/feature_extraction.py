import re
import time
from urllib import parse

from irwebcrawl.features.dictionary_construction import load_encoded_word_set
from irwebcrawl.features.scrape_cities import load_city_set
from irwebcrawl.features.trained_dictionary import load_trained_dict


def create_ngrams(token):
    if len(token) <= 5:
        return {token}

    ngrams = []

    for i in range(5, min(len(token), 20)):
        matches = re.finditer(f'(?=({"." * i}))', token)

        for match in matches:
            ngrams.append(match.group(1))

    ngrams.append(token)

    return ngrams


def extract_features(url):
    def update_counts(regex, url_part):
        nonlocal dict_count
        nonlocal city_count
        nonlocal trained_dict_count

        for token in re.split(regex, url_part):
            ngrams = create_ngrams(token)
            for ngram in ngrams:
                if ngram in word_set:
                    dict_count += 1
                if ngram in city_names:
                    city_count += 1
                if ngram in trained_dict:
                    trained_dict_count += 1

    split_tokens = re.compile('[&/\\-_\\s]')
    split_hostname_tokens = re.compile('[&/\\-_\\s.]')
    split_query_tokens = re.compile('[&/\\-_?=\\s]')
    split_fragment_tokens = re.compile('[&/\\-_#=\\s]')
    dict_count = 0
    city_count = 0
    trained_dict_count = 0

    word_set = load_encoded_word_set()
    city_names = load_city_set()
    trained_dict = load_trained_dict()
    parsed = parse.urlparse(url)

    dutch_domains = {'nl', 'be'}
    other_domains = {'net', 'org', 'com'}
    domain_code = parsed.hostname.split('.')[-1]
    if domain_code in dutch_domains:
        dutch_domain = 1
        other_domain = 0
    elif domain_code in other_domains:
        dutch_domain = 0
        other_domain = 1
    else:
        dutch_domain = 0
        other_domain = 0

    hyphen_count = url.count('-')

    update_counts(split_hostname_tokens, parsed.hostname.lower())
    update_counts(split_tokens, parsed.path.lower())
    update_counts(split_query_tokens, parsed.query.lower())
    update_counts(split_fragment_tokens, parsed.fragment.lower())

    '''
    print(f'Words in URL: {dict_count}')
    print(f'Cities in URL: {city_count}')
    print(f'Trained dict words: {trained_dict_count}')
    print(f'Dutch domain: {dutch_domain}')
    print(f'Other domain: {other_domain}')
    print(f'Hyphen count: {hyphen_count}')
    '''

    return [dutch_domain, other_domain, dict_count, city_count, trained_dict_count, hyphen_count]


class Extractor:
    def __init__(self):
        self.word_dict = load_encoded_word_set()
        self.city_dict = load_city_set()
        self.trained_dict = load_trained_dict()

    def extract_features_no_ngrams(self, url):
        def update_counts(regex, url_part):
            nonlocal dict_count
            nonlocal city_count
            nonlocal trained_dict_count

            for token in re.split(regex, url_part):
                if token in word_set:
                    dict_count += 1
                if token in city_names:
                    city_count += 1
                if token in trained_dict:
                    trained_dict_count += 1

        split_tokens = re.compile('[&/\\-_\\s]')
        split_hostname_tokens = re.compile('[&/\\-_\\s.]')
        split_query_tokens = re.compile('[&/\\-_?=\\s]')
        split_fragment_tokens = re.compile('[&/\\-_#=\\s]')
        dict_count = 0
        city_count = 0
        trained_dict_count = 0

        word_set = self.word_dict
        city_names = self.city_dict
        trained_dict = self.trained_dict
        parsed = parse.urlparse(url)

        dutch_domains = {'nl', 'be'}
        other_domains = {'net', 'org', 'com'}
        domain_code = parsed.hostname.split('.')[-1]
        if domain_code in dutch_domains:
            dutch_domain = 1
            other_domain = 0
        elif domain_code in other_domains:
            dutch_domain = 0
            other_domain = 1
        else:
            dutch_domain = 0
            other_domain = 0

        hyphen_count = url.count('-')

        update_counts(split_hostname_tokens, parsed.hostname.lower())
        update_counts(split_tokens, parsed.path.lower())
        update_counts(split_query_tokens, parsed.query.lower())
        update_counts(split_fragment_tokens, parsed.fragment.lower())

        return [dutch_domain, other_domain, dict_count, city_count, trained_dict_count, hyphen_count]

    def extract_features(self, url):
        def update_counts(regex, url_part):
            nonlocal dict_count
            nonlocal city_count
            nonlocal trained_dict_count

            for token in re.split(regex, url_part):
                ngrams = create_ngrams(token)
                for ngram in ngrams:
                    if ngram in word_set:
                        dict_count += 1
                    if ngram in city_names:
                        city_count += 1
                    if ngram in trained_dict:
                        trained_dict_count += 1

        split_tokens = re.compile('[&/\\-_\\s]')
        split_hostname_tokens = re.compile('[&/\\-_\\s.]')
        split_query_tokens = re.compile('[&/\\-_?=\\s]')
        split_fragment_tokens = re.compile('[&/\\-_#=\\s]')
        dict_count = 0
        city_count = 0
        trained_dict_count = 0

        word_set = self.word_dict
        city_names = self.city_dict
        trained_dict = self.trained_dict
        parsed = parse.urlparse(url)

        dutch_domains = {'nl', 'be'}
        other_domains = {'net', 'org', 'com'}
        domain_code = parsed.hostname.split('.')[-1]
        if domain_code in dutch_domains:
            dutch_domain = 1
            other_domain = 0
        elif domain_code in other_domains:
            dutch_domain = 0
            other_domain = 1
        else:
            dutch_domain = 0
            other_domain = 0

        hyphen_count = url.count('-')

        update_counts(split_hostname_tokens, parsed.hostname.lower())
        update_counts(split_tokens, parsed.path.lower())
        update_counts(split_query_tokens, parsed.query.lower())
        update_counts(split_fragment_tokens, parsed.fragment.lower())

        return [dutch_domain, other_domain, dict_count, city_count, trained_dict_count, hyphen_count]


if __name__ == '__main__':
    extractor = Extractor()
    # extract_features('https://www.doetinchem.nl/contact-en-openingstijden?origin=/contact?#view=bijles&kokosnoten-fryslannen')
    # extract_features('https://www.gemeentedoetinchem.nl/')

    start_time = time.time()
    result = extractor.extract_features('http://bca.cotesdarmor.fr/Default/Ermes/Recherche/Search.svc/SearchRss?q={%2522FacetFilter%2522:%2522{%5C%2522_298%5C%2522:%5C%2522Livre%2520lu%5C%2522,%5C%2522_27%5C%2522:%5C%2522Nouveaut%25C3%25A9%5C%2522}%2522,%2522PageRange%2522:3,%2522QueryString%2522:%2522*%2522,%2522ResultSize%2522:6,%2522ScenarioCode%2522:%2522CATALOGUE%2522,%2522ScenarioDisplayMode%2522:%2522display-standard%2522,%2522SearchTerms%2522:%2522%2522,%2522SortField%2522:null,%2522SortOrder%2522:0,%2522XslPath%2522:%2522Recherche/encart_search.xslt%2522,%2522UseCache%2522:true}')
    print(time.time() - start_time)
    print(result)
