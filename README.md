# isw-database
This repository contains Python scripts which enable the web scraping, databasing, and querying of publications from the [Institute of the Study of War](http://www.understandingwar.org/). Publication contents and metadata (title, publication date, etc.) are programatically parsed from ISW's website and inserted into a MongoDB document database. A Flask based API provides HTTP endpoint access for outside applications to query the database.

## Setup
Begin by cloning this repository and installing the required Python packages

```bash
# Clone this repository
git clone https://github.com/rhammell/isw-database.git

# Go into the repository
cd isw-database

# Install required modules
pip3 install -r requirements.txt
```

Open the `config.ini` configuration file and change the placeholder value `Your-Mongo-Connection-String` to the connection string of the MongoDB instance that will be used. 

Ex. `mongodb+srv://<user>:<password>@cluster0.mrqo0.mongodb.net/` if using a Mongo Atlas cloud database. 

```
[mongodb]
connection_string = Your-MongoDB-Connection-String
database_name = ISW
collection_name = Publications
```

The default database and collection names `ISW` and `Publicaitons` can be edited within this file. If the database and collection do not exist they will be automatically created in the configured MongoDB as documents are inserted. 


## Populating MongoDB

The `populate_db.py` script is used to scrape ISW publications and add them to the configured MongoDB. The script can be run at regular intervals to continually add the latest publication data to the database without creating duplicate entries.

By default the latest 20 ISW search pages (10 publications per page) are scraped. This number can be controlled with an optional integer number passed into the run command. 

```bash
# Run default 20 pages
python3 populate_db.py

# Run latest 10 pages
python3 populate_db.py 10
```

Each publication webpage is parsed to collect its text body and other metadata. Below is an example of the document structure for each publication added to the database. 

```python
{
    "_id": "782260080255bd77491caf3ad88282c976e54dfd", # Hash of title and date
    "title": "Iraq Situation Report: August 12-18, 2020",
    "date": "2020-08-21T17:38:31-04:00",
    "url": "http://www.understandingwar.org/backgrounder/iraq-situation-report-august-12-18-2020",
    "content": "Iraq Situation Report: August 12-18, 2020 | Institute for the ..."
}
```

## API Access

The `app.py` script creates a REST API that allows for querying the database through HTTP endpoints. This functionality enables other applications to get access the scraped publications data without direct connection to the database itself. 

Initialize the API server using on the default host and port (`localhost:5000`) with the following command

```bash
python3 app.py
```

### Endpoints

`GET /publications`: Returns a list of all publications data in the database

`GET /publicatins/<id>`: Returns the database entry

`GET /publications/latest`: Returns the 10 most recent publications ordered by their 'date' 

`POST /publications/search`: Accepts a JSON formatted MongoDB query that is passed to the database.  


### Examples







