"""Custom JSON encoders for MongoDB types."""
from bson import ObjectId
from pydantic import json


class MongoJSONEncoder(json.Encoder):
    """Custom JSON encoder that handles MongoDB ObjectId."""
    
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)
