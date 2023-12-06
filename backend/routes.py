from . import app
import os
import json
import pymongo
from flask import jsonify, request, make_response, abort, url_for, Flask  # noqa; F401
from pymongo import MongoClient
from bson import json_util
from pymongo.errors import OperationFailure
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
import sys

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "songs.json")
songs_list: list = json.load(open(json_url))

# client = MongoClient(
#     f"mongodb://{app.config['MONGO_USERNAME']}:{app.config['MONGO_PASSWORD']}@localhost")
mongodb_service = os.environ.get('MONGODB_SERVICE') #'localhost'
mongodb_username = os.environ.get('MONGODB_USERNAME')#'robi'
mongodb_password = os.environ.get('MONGODB_PASSWORD')#'321890As'
mongodb_port = os.environ.get('MONGODB_PORT')#'27017'

print(f'The value of MONGODB_SERVICE is: {mongodb_service}')

if mongodb_service == None:
    app.logger.error('Missing MongoDB server in the MONGODB_SERVICE variable')
    # abort(500, 'Missing MongoDB server in the MONGODB_SERVICE variable')
    sys.exit(1)

if mongodb_username and mongodb_password:
    url = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_service}"
else:
    url = f"mongodb://{mongodb_service}"


print(f"connecting to url: {url}")

try:
    client = MongoClient(url)
except OperationFailure as e:
    app.logger.error(f"Authentication error: {str(e)}")

db = client.songs
db.songs.drop()
db.songs.insert_many(songs_list)
songs=db.songs

def parse_json(data):
    return json.loads(json_util.dumps(data))

######################################################################
# INSERT CODE HERE
######################################################################
# app= Flask.app(__name__)
@app.route("/health")
def health_ind():
    return {"status":"ok"}

@app.route("/count")
def count_songs():
    return {"result":f"{songs.count_documents({})}"}, 200

@app.route("/song")
def songs_list():
    result=songs.find()
    return json_util.dumps(list(result)), 200


#test one
# @app.route("/test/<int:id>", methods=["PUT"])
# def upd_song(id):
#     data=request.json
#     f_id=id
#     return {"message":f"test {f_id}"},200

@app.route("/song/<int:id>", methods=['GET'])
def songs_by_id(id):
    result=songs.find_one({"id":id})
    return {"status":f"{result}"}, 200

@app.route("/song", methods=["POST"])
def create_song():
    data=request.json
    check = songs.find_one({"id":data["id"]})
    if check:
        return {"Message": f"song with id {data['id']} already present"}, 302
    songs.insert_one(data)
    return {"inserted_id":f"{songs.find_one({'id':data['id']}, {'_id':1})}"}, 201

@app.route("/song/<int:id>", methods=["PUT"])
def upd_song(id):
    data=request.json
    newvalues={"$set":data}
    song=songs.find_one({'id':id})
    
    if song:
        songs.update_one({'id':id}, newvalues)
        song=songs.find_one({'id':id})
        return {"message":f"{data}"}, 200
    
    return {'message':f'{song}'}, 404

@app.route("/song/<int:id>", methods=["DELETE"])
def delete_song(id):
    result = db.songs.delete_one({"id": id})
    if result.deleted_count == 0:
        return {"message": "song not found"}, 404
    else:
        return "", 204

