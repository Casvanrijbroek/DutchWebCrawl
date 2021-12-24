# Script made to scrape URLs from the DMOZ site on multiple threads

import urllib
from multiprocessing import Process
from bs4 import BeautifulSoup
import json


def descend(url: str):
    print("This shows something is working")
    try:
        url_contents = str(urllib.request.urlopen("https://dmoz-odp.org/" + url).read())
    except urllib.error.HTTPError as fof:  # 404 error handling
        return []
    soup = BeautifulSoup(url_contents, 'html.parser')

    # Getting subpages
    hrefs = []
    div_bs4 = soup.find('div', id="subcategories-div")
    if div_bs4 is not None:
        hrefs = [ref.get('href') for ref in div_bs4.findAll("a") if url in ref.get('href')]
    # Getting normal site links
    extra_links = []
    div_bs4 = soup.find('div', id="site-list-content")
    if div_bs4 is not None:
        extra_links += [ref.get('href') for ref in div_bs4.findAll("a", target="_blank")]

    # Getting more more links
    nested_links = []
    for link in hrefs:
        nested_links += descend(link)

    # returning all links
    return extra_links + nested_links


def first_descend(base_url, country):
    # Starting a thread for each category
    links = descend(base_url)
    with open('data'+country+'.json', 'w') as f:
        json.dump(links, f)

def main():

    # place the categories in the form of ["category", "name you'd like the file to have"]
    # E.G. ["World/Deutsch/", "german"], ["World/Fran%C3%A7ais/", "France"]

    links = []

    procs = []
    # instantiating process with arguments
    for link in links:
        proc = Process(target=first_descend, args=(link[0],link[1]))
        procs.append(proc)
        proc.start()
    # complete the processes
    for proc in procs:
        proc.join()


if __name__ == '__main__':
    main()

