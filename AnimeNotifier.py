import pickle
from time import sleep
import bs4
import requests

import sys
sys.setrecursionlimit(10000)

def getTimer(url):
    """Scrapes the site for the timer"""

    html = requests.get('http://9anime.to'+url)
    html.raise_for_status()
    soup = bs4.BeautifulSoup(html.text, 'html.parser')
    # print(soup.prettify())
    newSoup = soup.find('span', {'class': 'timer'})
    timer = newSoup.text
    commaSplitList = timer.split(',')

    hours = []
    days = []
    minutes = []
    days = commaSplitList[0]
    hours = commaSplitList[1]
    minutes = commaSplitList[2]

    daysSplit = int(days.split(' ')[0])
    hoursSplit = int(hours.split(' ')[1])
    minutesSplit = int(minutes.split(' ')[1])

    print(daysSplit, "days ", hoursSplit, "hours ", minutesSplit, "minutes ")

    # numberOfHours = int(hours[0])
    # numberOfMinutes = int(minutes[0])
    # print(numberOfDays)
    # print(numberOfHours)
    # for i in commaSplit:
    #     spaceSplit = commaSplit.split(' ')
    #     print(spaceSplit)

def merge_pickles(pkl1, pkl2, mergedpkl):
    """Merges two pickle files into one"""

    with open(pkl1, 'rb') as file:
        dic1 = pickle.load(file)
        file.close()
    with open(pkl2, 'rb') as file:
        dic2 = pickle.load(file)
        file.close()
    merge = {**dic1, **dic2}
    with open(mergedpkl, 'wb') as file:
        pickle.dump(merge, file)
        file.close()


def read_pickle(pkl):
    """Reads the merged pickle file to look for desired anime"""

    with open(pkl, 'rb') as file:
        dict = pickle.load(file)
        file.close()
    return dict


def write_pickle(data, pkl):
    """Writes the data into individual pickle file"""

    with open(pkl, 'wb') as file:
        pickle.dump(data, file)
        file.close()


def get_html(url, pageNumber):
    """Downloads the html and returns the text within"""

    htmlPage = ""
    flag = True
    while flag:
        try:
            htmlPage = requests.get(url)
            htmlPage.raise_for_status()  # Checking for errors
        except:
            print(f"Retrying to access page number {pageNumber}")
            sleep(2)
            continue
        else:
            # print(htmlPage.text)
            flag = False
    if htmlPage:
        return htmlPage.text


def scrape_pages(start, end, pklfile):
    """Scrapes the site for list of animes and their corresponding links"""

    pageNumber = start
    linkList = []
    nameList = []
    animeDictionary = {}

    while pageNumber <= end:  # Max Pages = 424
        print(f"Scraping page number: {pageNumber}")
        url = 'https://9anime.to/az-list?page=' + str(pageNumber)

        # Converting to Beautiful soup
        soup = bs4.BeautifulSoup(get_html(url, pageNumber), 'html.parser')

        # Looking for all anime names on the page
        findingListOfNames = soup.findAll('a', {'class': 'name'})

        # Looking for all links to the animes on the page
        findingListOfLinks = soup.findAll('a', {'class': 'name'})

        # Storing all links in a list named linkList
        for i in findingListOfLinks:
            linkList.append(i.get('href'))

        # Storing all anime names in a list named nameList
        for i in findingListOfNames:
            nameList.append(str(i.contents[0]))

        # Setting up a dictionary of anime names with their corresponding links
        for i, j in zip(nameList, linkList):
            if type(i) == str and type(j) == str:
                animeDictionary[i.lower()] = j
            else:
                print(type(i),type(j))

        # Incrementing the page number
        pageNumber += 1

    write_pickle(animeDictionary, pklfile)


if __name__ == "__main__":
    saved_pkl = "AnimeList"
    flag = False

    # scrape_pages(1, 2, saved_pkl)

    animeDictionary = read_pickle(saved_pkl)

    desiredAnime = input("Which anime do you want to follow: ")
    for key in animeDictionary.keys():
        if desiredAnime.lower() in key.lower():
            getTimer(animeDictionary[desiredAnime])
            # print(animeDictionary[desiredAnime])
            flag = False
            break
        else:
            flag = True
    if flag:
        print("Your desired anime doesn't exist. BAKA!")

