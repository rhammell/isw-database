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
pip install -r requirements.txt
```

Open the `config.ini` configuration file and change the placeholder value `Your-Mongo-Connection-String` to the connection string of the MongoDB that will be used.

```
[mongodb]
connection_string = Your-MongoDB-Connection-String
```

Ex. `mongodb+srv://<user>:<password>@cluster0.mrqo0.mongodb.net/` if using a Mongo Atlas cloud database. 

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

Documents are inserted into a `Publications` collection within a `ISW` database in the configured MongoDB. These will be programmatically created when documents are inserted if they do not already exist.