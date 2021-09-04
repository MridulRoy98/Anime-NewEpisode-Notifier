import os
import pickle
import re
from time import sleep
import bs4
import requests
import sys
from datetime import datetime
from datetime import timedelta

sys.setrecursionlimit(10000)


def getTimer(url, desiredAnime, followed_pkl):
    """Scrapes the site for the timer"""

    html = requests.get('http://9anime.to' + url)
    html.raise_for_status()
    soup = bs4.BeautifulSoup(html.text, 'html.parser')
    try:
        newSoup = soup.find('span', {'class': 'timer'})
        strTimer = newSoup.text
        setTargetTime(desiredAnime, strTimer)

    except:
        print("The Anime has finished airing")

    # followedDictionary[desiredAnime] = strTimer
    # write_pickle(followedDictionary, followed_pkl)
    # print(re.findall("\d+",timer)) # Regex to get digits from the timer
    # print(strTimer)


def setTargetTime(desiredAnime, strTimer):
    '''Converts and writes the anime episode airing date-time'''

    commaSplitList = strTimer.split(',')

    # Getting Digits from the strTimer
    days = commaSplitList[0]
    hours = commaSplitList[1]
    minutes = commaSplitList[2]

    # Converting them to integers
    daysSplit = int(days.split(' ')[0])
    hoursSplit = int(hours.split(' ')[1])
    minutesSplit = int(minutes.split(' ')[1])

    targetDate = datetime.now() + timedelta(days=daysSplit, hours=hoursSplit, minutes=minutesSplit)

    # Readable format i.e.(2021-09-04 19:35:14),
    # NOTE TO SELF: Replace '%H' with '%I' for 12 hour format
    formatedTargetDate = targetDate.strftime('%Y/%m/%d %H:%M:%S')

    # Adding to a Dictionary
    # Using desired anime as key and the target date+time as value
    followedDictionary[desiredAnime] = formatedTargetDate

    # writing the dictionary in a pickle file
    write_pickle(followedDictionary, followed_pkl)
    print(f"it will air on - {followedDictionary[desiredAnime]}, - in exactly {strTimer}.")
    # print('\n')
    # for i, j in followedDictionary.items():
    #     print(i, "--will air on: ", j)
    countdown(desiredAnime, followed_pkl)


def checkForAnime(desiredAnime, animeDictionary, followedDictionary):
    flag = False
    followedFlag = False
    for key in followedDictionary.keys():
        if desiredAnime in key.lower():
            remaining = countdown(desiredAnime, followed_pkl)
            # getTimer(animeDictionary[desiredAnime], desiredAnime, followed_pkl)
            print("You are already following this anime, it will air on - ", followedDictionary[key],
                  f" - in exactly {remaining} seconds")
            followedFlag = True
            break
    if not followedFlag:
        for key in animeDictionary.keys():
            if desiredAnime in key.lower():
                getTimer(animeDictionary[desiredAnime], desiredAnime, followed_pkl)

                # print(animeDictionary[desiredAnime])
                flag = False
                break
            else:
                flag = True

    if flag:
        print("Your desired anime doesn't exist. BAKA!")


def countdown(desiredAnime, followed_pkl):
    loadedfile = read_pickle(followed_pkl)
    date_time_str = loadedfile[desiredAnime]
    date_time_obj = datetime.strptime(date_time_str, '%Y/%m/%d %H:%M:%S')
    currentTime = datetime.now()
    time_delta = (date_time_obj - currentTime)

    # Converting to seconds
    days, seconds = time_delta.days, time_delta.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60 + (hours * 60)
    seconds = (seconds % 60) + (minutes * 60)

    return seconds


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
                print(type(i), type(j))

        # Incrementing the page number
        pageNumber += 1

    write_pickle(animeDictionary, pklfile)


if __name__ == "__main__":

    saved_pkl = "AnimeList.pkl"
    followed_pkl = "Following.pkl"
    followedDictionary = {}
    animeDictionary = read_pickle(saved_pkl)
    if os.path.isfile('Following.pkl'):
        followedDictionary = read_pickle(followed_pkl)

    while True:

        # Following line is only for scraping again
        # scrape_pages(1, 2, saved_pkl)

        animeName = input("Which anime do you want to follow: ")
        if animeName == '-1':
            break

        desiredAnime = animeName.lower()
        checkForAnime(desiredAnime, animeDictionary, followedDictionary)
        print()
