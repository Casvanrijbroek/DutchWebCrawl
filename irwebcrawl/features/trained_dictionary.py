import json
import re
from urllib import parse
import pickle


def create_trained_dict():
    data1 = open('../urls/dutch_urls.json')
    data2 = open('../urls/not_dutch_urls.json')
    dutch = json.load(data1)
    non_dutch = json.load(data2)
    delimiters = "=", "&", "#", "?", ",", "/", ",", "'", ".", "://", "-"
    url = "http://www.internetwordstats.com/africa2.nl"
    split = '|'.join(map(re.escape, delimiters))

    url_split = re.split(split, url)
    count = {}

    forbidden = {'nl', 'be', 'sr', 'org', 'net', 'com', 'www'}
    inverse_tf = {}
    inverse_tf2 = {}

    for j in range(len(dutch)):
        split_regex = re.compile('[&/\\-_\\s.?#=]')
        tokens = set()
        parsed = parse.urlparse(dutch[j])
        tokens.update(set(re.split(split_regex, parsed.hostname.lower())))
        tokens.update(set(re.split(split_regex, parsed.path.lower())))
        tokens.update(set(re.split(split_regex, parsed.query.lower())))
        tokens.update(set(re.split(split_regex, parsed.fragment.lower())))
        tokens.discard('')

        for token in tokens:
            if token not in forbidden:
                try:
                    count = inverse_tf[token]
                    count += 1
                    inverse_tf[token] = count
                except KeyError:
                    inverse_tf[token] = 1

    for j in range(len(non_dutch)):
        split_regex = re.compile('[&/\\-_\\s.?#=]')
        tokens = set()
        parsed = parse.urlparse(non_dutch[j])
        tokens.update(set(re.split(split_regex, parsed.hostname.lower())))
        tokens.update(set(re.split(split_regex, parsed.path.lower())))
        tokens.update(set(re.split(split_regex, parsed.query.lower())))
        tokens.update(set(re.split(split_regex, parsed.fragment.lower())))
        tokens.discard('')

        for token in tokens:
            if token not in forbidden:
                try:
                    count = inverse_tf2[token]
                    count += 1
                    inverse_tf2[token] = count
                except KeyError:
                    inverse_tf2[token] = 1

    print(f'unique dutch tokens: {len(inverse_tf)}')
    print(f'unique non-dutch tokens: {len(inverse_tf2)}')
    print(f'# dutch urls: {len(dutch)}')
    print(f'# non-dutch urls: {len(non_dutch)}')
    cut = 0.0001 * len(dutch)

    print(f'cut-off: {cut}')

    words = set()

    for token in inverse_tf:
        if inverse_tf[token] > cut:
            words.add(token)
    keep = set()

    for token in words:
        if not token in inverse_tf2:
            keep.add(token)
            continue

        dutch_count = inverse_tf[token]
        nondutch_count = inverse_tf2[token]
        total = dutch_count + nondutch_count

        if dutch_count > (total * 0.8):
            keep.add(token)

    remove = set()

    for token in keep:
        if len(token) < 3:
            if token != 'bv' and token != 'op':
                remove.add(token)

    keep.difference_update(remove)

    print(f'# of tokens after filtering: {len(keep)}')

    with open('../pickles/trained_dict.p', 'wb') as output_handle:
        pickle.dump(keep, output_handle)


def load_trained_dict():
    with open('../pickles/trained_dict.p', 'rb') as input_handle:
        trained_dict = pickle.load(input_handle)

    return trained_dict


if __name__ == '__main__':
    create_trained_dict()
