# isw-database
This repository contains Python scripts which enable the web scraping, databasing, and querying of publications from the [Institute of the Study of War](http://www.understandingwar.org/). 

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

The `populate_db.py` script is used to scrape ISW publications and add them to the configured MongoDB. Run the script with the following command.

```bash
python3 populate_db.py
```