# Imports the Google Cloud client library
from google.cloud import storage
from os.path import dirname

base_dir = dirname(dirname(__file__))

# Instantiates a client
storage_client = storage.Client.from_service_account_json(
   base_dir+'/'+'wordcloud_creds.json')
# The name for the new bucket
bucket_name = "wordcloud_ftp"

# Creates the new bucket
bucket = storage_client.create_bucket(bucket_name)

print("Bucket {} created.".format(bucket.name))