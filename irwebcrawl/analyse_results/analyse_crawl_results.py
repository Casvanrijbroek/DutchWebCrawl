import json
from urllib import parse
import random
import webbrowser
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score


def main():
    analyse_single_crawl('../dutch_spider.json')
    print('-' * 50)
    analyse_single_crawl('../dutch_spider_BFO.json')
    print('-' * 50)
    analyse_single_crawl('../dutch_spider_BFO_limit2.json')
    print('-' * 50)
    analyse_single_crawl('../dutch_spider_limit2.json')
    print('-' * 50)


def calculate_test_metrics(filepath):
    entries = read_output(filepath)
    predictions = [0 if entry['prediction'] == 'False' else 1 for entry in entries]
    true_labels = [0 if entry['true_label'] == 'False' else 1 for entry in entries]

    accuracy = accuracy_score(true_labels, predictions)
    f_measure = f1_score(true_labels, predictions)
    precision = precision_score(true_labels, predictions)
    recall = recall_score(true_labels, predictions)

    print(f'Accuracy: {accuracy}')
    print(f'F-measure: {f_measure}')
    print(f'Precision: {precision}')
    print(f'Recall: {recall}')


def merge_test_urls(path1, path2):
    urls1 = read_output(path1)
    urls2 = read_output(path2)

    urls1.extend(urls2)
    write_json(urls1, 'clean_curated_test_urls.json')


def convert_lex_to_cas(filepath):
    entries = read_output(filepath)
    seen_urls = set()

    for entry in entries:
        if entry['url'] in seen_urls:
            entries.remove(entry)
        else:
            seen_urls.add(entry['url'])

    for entry in entries:
        if entry['label'] == 'Error':
            entries.remove(entry)

    for entry in entries:
        entry['true_label'] = entry['label']
        del entry['label']

    write_json(entries, 'clean_curated_test_urls_lex.json')


def clean_curated_urls(filepath):
    entries = read_output(filepath)

    for entry in entries:
        if entry['true_label'] == 'Error':
            entries.remove(entry)
        elif entry['true_label'] != 'True' and entry['true_label'] != 'False':
            print(entry['url'])
            print(entry['prediction'])
            print(entry['true_label'])
            sentinel = True

            while sentinel:
                new_label = input('give true label: ')
                if new_label == 'True' or new_label == 'False':
                    entry['true_label'] = new_label
                    sentinel = False
                else:
                    print('wrong label format')

    write_json(entries, 'clean_curated_test_urls_cas.json')


def analyse_test_urls(filepath):
    test_urls = read_output(filepath)
    for entry in test_urls:
        webbrowser.open(entry['url'])
        print(entry['url'])
        print(f'prediction: {entry["prediction"]}')
        true_label = input('label: ')

        if true_label == 'stop':
            break

        print('-' * 50)

        entry['true_label'] = true_label

    write_json(test_urls, 'curated_test_urls_cas.json')


def sample_test_urls(urls, domains, predictions):
    index_list = list(range(0, len(urls)))
    random.Random(42).shuffle(index_list)
    picked_urls = []
    seen_domains = set()

    for index in index_list:
        if domains[index] not in seen_domains:
            picked_urls.append({'url': urls[index],
                                'prediction': predictions[index]})
            seen_domains.add(domains[index])
            if len(picked_urls) == 1000:
                break

    urls_cas = picked_urls[:500]
    urls_lex = picked_urls[500:]

    write_json(urls_cas, '../test_urls_cas.json')
    write_json(urls_lex, '../test_urls_lex.json')


def analyse_single_crawl(filepath):
    content = read_output(filepath)
    urls = [entry['href'] for entry in content]
    domains, unique_domains_set = unique_domains(urls)

    print(f'Statistics for {filepath.split("/")[-1]}')
    print(f'# of urls: {len(urls)}')
    print(f'# of unique domains: {len(unique_domains_set)}')
    print(f"# of nl.wikipedia.org: {domains.count('nl.wikipedia.org')}")


def unique_domains(url_list):
    domains = [parse.urlparse(url).hostname for url in url_list]
    unique_domains_set = set(domains)

    return domains, unique_domains_set


def read_output(filepath):
    with open(filepath, 'r') as input_handle:
        content = json.load(input_handle)

    return content


def write_json(content, filepath):
    with open(filepath, 'w') as output_handle:
        json.dump(content, output_handle)


if __name__ == '__main__':
    calculate_test_metrics('clean_curated_test_urls.json')
