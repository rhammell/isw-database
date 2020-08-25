''' Flask based HTTP endpoints for database access '''

from configparser import ConfigParser

from flask import Flask
from flask_pymongo import PyMongo
from flask_restful import Api, Resource, reqparse


# Read MongoDB configuration settings
config = ConfigParser()
config.read('config.ini')
connection_string = config['mongodb']['connection_string']
database_name = config['mongodb']['database_name']
collection_name = config['mongodb']['collection_name']

# Initiate App
app = Flask(__name__)

# Initiate Mongo connection - database name needed in URI
app.config["MONGO_URI"] = connection_string + database_name
app.config["MONGO_DBNAME"] = database_name
mongo = PyMongo(app)

# Initiate API
api = Api(app)


class PublicationsList(Resource):
    ''' Return list of publications from database '''

    def get(self):

      # Query DB
      data = []
      cursor = mongo.db[collection_name].find({}).sort("date", -1)
      for doc in cursor:
          data.append(doc)

      return {"response": data}


class PublicationsId(Resource):
    ''' Return publication defined by doc_id '''

    def get(self, doc_id):

      # Query DB
      data = mongo.db[collection_name].find_one({'_id': doc_id})

      return {"response": data}


class PublicationsLatest(Resource):
    ''' Return list of 10 latest publications ordered by date '''

    def get(self):

      # Query DB
      data = []
      cursor = mongo.db[collection_name].find({}).sort("date", -1).limit(10)
      for doc in cursor:
          data.append(doc)

      return {"response": data}


class Search(Resource):
  ''' Search the connected database using a provided query object 
      that is supplied in the reqest 
  '''

  def __init__(self):

      # Define required request parameters
      self.reqparse = reqparse.RequestParser()
      self.reqparse.add_argument('query', type=dict, help='No query object provided')

      super(Search, self).__init__()


  def post(self):

      # Get data passed in request
      args = self.reqparse.parse_args()

      # Perform query on DB
      data = []
      cursor = mongo.db[collection_name].find(args['query'])
      for doc in cursor:
          data.append(doc)

      return {"response": data}


# Add resource endpoints
api.add_resource(PublicationsList, "/publications")
api.add_resource(PublicationsId, "/publications/<string:doc_id>")
api.add_resource(PublicationsLatest, "/publications/latest")
api.add_resource(Search, "/publications/search")


if __name__ == '__main__':

    # Start app 
    app.run(debug=True)