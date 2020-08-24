''' 
    Python 3+

    Scrape publications from understandingwar.com and push data into a MongoDB.
'''

import sys
import requests
import hashlib
from bs4 import BeautifulSoup 
from pymongo import MongoClient
from configparser import ConfigParser


def get_publications(url):
    ''' Return list of publication urls found on input page '''

    # Request page contents
    r = requests.get(url)

    # Parse html
    soup = BeautifulSoup(r.text,'html.parser')

    # Find hrefs with divs
    divs = soup.find_all('div', {'class': 'field-content'})
    hrefs = ['http://www.understandingwar.org' + div.find('a').get('href') for div in divs]

    return hrefs


def get_date(soup):
    ''' Return submitted date from parsed publication '''

    try:
      date = soup.find('span',{'property':'dc:date dc:created'}).get('content')
    except:
      date = ''

    return date


def get_title(soup):
    ''' Return title from parsed publication '''

    try:
      title = soup.find('h1',{'class':'title'}).text
    except:
      title = ''
    
    return title


def get_contents(soup):
    ''' Return text content of parsed publication '''

    try:
      parents_blacklist = ['[document]','html','head','style','script','body','div','a','section','tr','td','label','ul','header','aside',]
      content = ''
      text = soup.find_all(text=True)
    
      for t in text:
        if t.parent.name not in parents_blacklist and len(t) > 10:
          content=content+t+' '

    except:
      content = ''

    return content


def parse_publication(url):
    ''' Parse the contents of a publication page and return the contents
        and metadata as a dictionary.
    '''

    # Initate output 
    data = {}

    # request page contents
    r = requests.get(url)

    # Parse html 
    soup = BeautifulSoup(r.text,'html.parser')

    # Get data
    data['url'] = url
    data['title'] = get_title(soup)
    data['date'] = get_date(soup)
    data['content'] = get_contents(soup)

    # Generate unique id value - this will prevent duplicates being inserted
    # into the DB when running this script repeatedly
    ustring = data['title'] + data['date']
    data['_id'] = hashlib.sha1(ustring.encode()).hexdigest()

    return data


def main(n_pages=20):
    ''' Process publications from the web and insert into database '''

    # Read configuration file
    config = ConfigParser()
    config.read('config.ini')

    # Create MongoDB client using configured conneciton string
    connection_string = config['mongodb']['connection_string']
    client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)

    # Test DB connection
    try: 
        client.server_info()
    except:
        print("MongoDB connection failed. Check configured connection string: {}".format(connection_string))
        return

    # Define database and collection to use
    db = client["ISW"]
    collection = db["Publications"]

    # Get list of ISW page urls
    base_url = 'http://www.understandingwar.org/publications'
    page_urls = [base_url + '?page={}'.format(i) for i in range(n_pages)]

    # Get list publication urls from pages
    publication_urls = []
    print(' ')
    for i, page_url in enumerate(page_urls):
        print('Parsing page {} of {}: {}'.format(i+1, len(page_urls), page_url))

        publication_urls.extend(get_publications(page_url))

    # Initialize number of docs inserted into DB
    n_inserted = 0

    # Loop through each publication url
    print(' ')
    for i, publication_url in enumerate(publication_urls): 
        print('Parsing publication {} of {}: {}'.format(i+1, len(publication_urls), publication_url))

        # Parse data from publicaiton url
        doc = parse_publication(publication_url)
        
        # Insert doc into collection - use update_one and upsert to prevent 
        # creating duplicate entries in the DB
        res = collection.update_one(
            {'_id':doc['_id']}, 
            {"$set": doc}, 
            upsert=True
        )

        # Count successfully inserted docs
        if res.upserted_id:
            n_inserted += 1
            print('  Successfully inserted into collection.')
        else: 
            print('  Already exists in collection. No insertion preformed.')

    print(' ')
    print('Processing complete. {} new documents inserted into the DB.'.format(n_inserted))


if __name__ == "__main__":

    # Run main function
    if len(sys.argv) == 2:
      main(n_pages=int(sys.argv[1]))
    else:
      main()



