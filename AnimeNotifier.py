import bs4
import requests
pageNumber = 1
nameList = []
while pageNumber <= 1:
    htmlPage = requests.get('https://9anime.to/az-list?page='+str(pageNumber))
    htmlPage.raise_for_status()
    soup = bs4.BeautifulSoup(htmlPage.text, 'html.parser')
    findingList = soup.findAll('a', {'class': 'name'})
    for i in findingList:
        nameList = i.contents[0]
        print(nameList)
    pageNumber += 1