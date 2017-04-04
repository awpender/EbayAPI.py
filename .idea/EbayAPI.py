from bs4 import BeautifulSoup
import csv
import json
import pandas as pd
import requests
import re
import sys



headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko)' 'Chrome/41.0.2227.1 Safari/537.36'}

counter = 1
counting = 1
increment = 0
total_products = []
going_to = 50
dowhat = int(input('Enter 1 for links only or 2 for all info: '))
username = input("What is the Ebay username: ")

def pageInfo(array_length, page_number):
    '''This function writes output to keep track of length written and page number'''
    length = len(complete_titles) - 1
    print(f"Taking {length+1} products from page number {counting}")

while True:
    with open('CompleteLinks.csv', 'a', newline='', encoding='utf-8') as csv_file:
        csv_app = csv.writer(csv_file)
        csv_app.writerow(['Titles', 'URL'])
        while increment <= going_to:
            # Make links and title blank for each of the iterations of the loop
            complete_links = []
            complete_titles = []
            url = 'http://www.ebay.com.au/sch/m.html?_nkw=&_armrs=1&_from=&_ssn='+str(username)+'&_sop=10&_pgn='+str(counting)+'&_skc='+str(increment)+'&rt=nc'

            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.content, 'html.parser')
            # This finds the title of each of the products on the page
            urls = soup.find_all('h3', {'class': 'lvtitle'})
            # This finds the total number of products on the suppliers page
            if total_products:
                pass
            else:
                total_products = soup.find_all('span', {'class': 'rcnt'})
                going_to = int(total_products[0].text.replace(',',''))

            for anchor in urls:
                links = anchor.find_all('a')
                for a in links:
                    complete_links.append(a['href'])
                    complete_titles.append(a.text)

            length = len(complete_titles) - 1
            while length >= 0:
                csv_app.writerow([complete_titles[length]] + [complete_links[length]])
                length -= 1

            pageInfo(complete_titles, counting)
            counting += 1
            increment += 50
    if dowhat == 1:
        break
    xl = pd.read_csv(str(sys.path[0]) + '\CompleteLinks.csv')
    total_products = len(xl['URL'])

    with open('CompleteListings.csv', 'a', newline='', encoding='utf-8') as csv_file:

        csv_app = csv.writer(csv_file)
        csv_app.writerow(['URL', 'SKU', 'ItemID', 'StartDate', 'EndDate', 'Title', 'Description', 'Price', 'Sold', 'PageViews', 'Categories', 'Images'])


        for ebay in xl['URL']:
            image_urls = ''

            #Take the ebay ID from the URL
            m = re.search('/\d{12}\?', ebay)

            new_url = 'http://open.api.ebay.com/shopping?callname=GetSingleItem&IncludeSelector=Details,Description,TextDescription&responseencoding=JSON&appid=AndrewPe-Python-PRD-0240e526c-f92f10f9&siteid=0&version=939&ItemID=' + str(m.group(0)[1:-1])

            # pull json from api
            r = requests.get(url=new_url)
            info = r.json()

            # sku is not included in every pull
            try:
                js_sku = info['Item']['SKU']
            except KeyError:
                js_sku = ''

            # filter fields within the json
            js_url = info['Item']['ViewItemURLForNaturalSearch']
            js_id = info['Item']['ItemID']
            js_title = info['Item']['Title']
            js_description = info['Item']['Description']
            js_price = info['Item']['CurrentPrice']['Value']
            js_sold = info['Item']['QuantitySold']
            js_category = info['Item']['PrimaryCategoryName']

            # Removing time as we only need the date
            js_start = info['Item']['StartTime'].split('T')[0]
            js_end = info['Item']['EndTime'].split('T')[0]

            try:
                js_hits = info['Item']['HitCount']
            except KeyError:
                js_hits = ''
            js_images = info['Item']['PictureURL']

            for images in js_images:
                image_urls = image_urls + '|' + images

            csv_app.writerow([js_url] + [js_sku] + [js_id] + [js_start] + [js_end] + [js_title] + [js_description] + [js_price] + [js_sold] + [js_hits] + [js_category] + [image_urls])

            #Tracking % complete
            print('{}% Complete'.format(round(counter/total_products * 100, 2)))
            counter += 1
