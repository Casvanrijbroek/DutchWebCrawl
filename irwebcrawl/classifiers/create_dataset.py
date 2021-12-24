import json

import pandas as pd

from irwebcrawl.features.feature_extraction import Extractor


def create_dataset():
    dutch_urls = load_json('../urls/dutch_urls.json')
    non_dutch_urls = load_json('../urls/not_dutch_urls.json')

    dutch_features = create_feature_vectors(dutch_urls)
    dutch_df = pd.DataFrame(dutch_features, columns=['dutch_domain', 'other_domain', 'dict_count',
                                                     'city_count', 'trained_dict_count', 'hyphen_count'])
    dutch_df['y'] = [1 for _ in range(len(dutch_df))]

    non_dutch_features = create_feature_vectors(non_dutch_urls)
    non_dutch_df = pd.DataFrame(non_dutch_features, columns=['dutch_domain', 'other_domain', 'dict_count',
                                                             'city_count', 'trained_dict_count', 'hyphen_count'])
    non_dutch_df['y'] = [0 for _ in range(len(non_dutch_df))]

    final_df = pd.concat([dutch_df, non_dutch_df], ignore_index=True)
    final_df.to_csv('ngram_features.csv', index=False)


def create_feature_vectors(urls):
    extractor = Extractor()

    result = list(map(extractor.extract_features, urls))

    return result


def load_json(path):
    with open(path, 'r') as input_handle:
        content = json.load(input_handle)

    return content


if __name__ == '__main__':
    create_dataset()
