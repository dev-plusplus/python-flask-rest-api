def serialize_mongo_id(mongo_row):
    mongo_row['_id'] = str(mongo_row['_id'])
    return mongo_row