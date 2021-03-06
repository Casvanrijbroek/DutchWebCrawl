import pickle
import re
from urllib import parse

import requests
from bs4 import BeautifulSoup
import os


def create_city_set():
    response = requests.get('https://nl.wikipedia.org/wiki/Lijst_van_Nederlandse_plaatsen')
    soup = BeautifulSoup(response.text, 'html.parser')
    regex = re.compile('[A-Z].+')
    split_regex = re.compile('[-\\s]')

    all_links = soup.find(id="bodyContent").find_all("a")

    contents = list()
    names = set()

    for link in all_links:
        content = str(link.string)
        if regex.match(content):
            contents.append(content)

    contents = contents[5:-8]

    for content in contents:
        for name in re.split(split_regex, content.replace('(', '').replace(')', '').lower()):
            names.add(parse.quote(name))

    names.update(create_flemish_city_set())
    names.remove('')

    root_dir = os.path.abspath(os.path.dirname(__file__))
    cities_path = os.path.join(root_dir, '../pickles/cities.p')

    with open(cities_path, 'wb') as output_handle:
        pickle.dump(names, output_handle)


def create_flemish_city_set():
    response = requests.get('https://nl.wikipedia.org/wiki/Lijst_van_gemeenten_in_het_Vlaams_Gewest')
    soup = BeautifulSoup(response.text, 'html.parser')
    split_regex = re.compile('[,-]')

    table = soup.find('table', {'class': 'wikitable sortable'})

    names = set()

    for tr in table.find_all('tr'):
        tds = tr.find_all('td')

        if len(tds) > 0:
            cities = re.split(split_regex, tds[5].text.rstrip().lower().replace(' ', ''))

            for city in cities:
                names.add(parse.quote(city))

    return names


def load_city_set():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    cities_path = os.path.join(root_dir, '../pickles/cities.p')

    with open(cities_path, 'rb') as input_handle:
        names = pickle.load(input_handle)

    return names


if __name__ == '__main__':
    create_city_set()
