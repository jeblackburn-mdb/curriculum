import time

from pymongo.operations import SearchIndexModel

import key_param
from pymongo import MongoClient
import voyageai
from datasets import load_dataset

from key_param import embedding_model

docs = load_dataset("MongoDB/mongodb-docs")
chunked_docs = load_dataset("MongoDB/mongodb-docs-embedded")

vo = voyageai.Client(api_key=key_param.voyage_api_key)

# Initialize a MongoDB Python client
mongodb_client = MongoClient(key_param.mongodb_uri)

#  Database name
DB_NAME = "ai_agents"
# Name of the collection with full documents- used for summarization
FULL_COLLECTION_NAME = "full_docs"
# Name of the collection for vector search- used for Q&A
VS_COLLECTION_NAME = "chunked_docs"
# Name of the vector search index
VS_INDEX_NAME = "vector_index"


db = mongodb_client[DB_NAME]
vs_collection = db[VS_COLLECTION_NAME]
full_collection = db[FULL_COLLECTION_NAME]

# for doc in docs["train"]:
#     # Insert the document into the full_docs collection
#     full_collection.insert_one(doc)

# vs_collection.insert_many(docs["train"])

# for chunked_doc in chunked_docs["train"]:
#     embedding = vo.embed(chunked_doc["body"], model=embedding_model, input_type="document", output_dimension=1024).embeddings[0]
#     print(chunked_doc["body"][:99])
#     print(embedding[:9])
#     chunked_doc["embedding"] = embedding
#     vs_collection.insert_one(chunked_doc)
    

# Create your index model, then create the search index
search_index_model = SearchIndexModel(
  definition={
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "numDimensions": 1024,
        "similarity": "dotProduct"
      }
    ]
  },
  name="vector_index",
  type="vectorSearch"
)
result = vs_collection.create_search_index(model=search_index_model)
print("New search index named " + result + " is building.")
# Wait for initial sync to complete
print("Polling to check if the index is ready. This may take up to a minute.")
predicate=None
if predicate is None:
  predicate = lambda index: index.get("queryable") is True
while True:
  indices = list(vs_collection.list_search_indexes(result))
  if len(indices) and predicate(indices[0]):
    break
  time.sleep(5)
print(result + " is ready for querying.")

# vs_collection.create_search_index(model=model)