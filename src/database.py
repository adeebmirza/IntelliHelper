from pymongo import MongoClient
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.exception import CustomException
from bson import ObjectId
from src.logger import logger
load_dotenv()

try:
    client = MongoClient("mongodb://localhost:27017")
    db = client['IntelliHelper']
    users_collection = db['users']
except Exception as e:
    raise CustomException(e,sys)


def create_user(user_data):
    logger.info("Creating user")
    try:
        users_collection.insert_one(user_data)
    except Exception as e:
        raise CustomException(e,sys)

def find_user(login_input):
    logger.info("Finding user")
    try:
        return users_collection.find_one({"$or": [{"username": login_input}, {"email": login_input}]})
    except Exception as e:
        raise CustomException(e,sys)
    
def get_user_by_id(user_id):
    """Retrieve user by their ObjectId."""
    return users_collection.find_one({'_id': ObjectId(user_id)})