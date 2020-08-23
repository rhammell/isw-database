''' 
    Scrape publications from understandingwar.com and push data into a MongoDB.
    Articles are augmented parsing names and geocoding locations.
'''

import requests
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
        and metadata as a dictionary. Augment data with NLP and geocoding. 
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


    return data


def main():
    ''' Process publications from the web and insert into database '''

    # Read configuration file
    config = ConfigParser()
    config.read('config.ini')

    # Create MongoDB client with configured conneciton string
    connection_string = config['mongodb']['connection_string']
    client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)

    # Test DB connection
    try: 
        client.server_info()
    except:
        print("MongoDB connection failed. Check configured connection string: {}".format(connection_string))
        return

    # Get list of ISW publications page urls
    base_url = 'http://www.understandingwar.org/publications'
    n_pages = 20
    page_urls = [base_url + '?page={}'.format(i) for i in range(1)]

    # Get list publication urls from pages
    publication_urls = []
    for i, page_url in enumerate(page_urls):
        print('Parsing page {} of {}: {}'.format(i+1, len(page_urls), page_url))

        publication_urls.extend(get_publications(page_url))

    # Initiate list of docs for db
    docs = []

    # Loop through each publication
    for i, publication_url in enumerate(publication_urls): 
        print('Parsing publication {} of {}: {}'.format(i+1, len(publication_urls), publication_url))

        # Parse data from publicaiton
        doc = parse_publication(publication_url)
        docs.append(doc)

    # Insert docs into Publications collection
    db = client["ISW"]
    collection = db["Publications"]
    collection.insert_many(docs)

    print('Processing complete.')


if __name__ == "__main__":

    # Run main function
    main()



