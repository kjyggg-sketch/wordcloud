from google.cloud import storage
from os.path import dirname
import os

def upload_to_bucket(blob_name, path_to_file, bucket_name):
    """ Upload data to a bucket"""

    # Explicitly use service account credentials by specifying the private key
    # file.

    storage_client = storage.Client.from_service_account_json(
        'wordcloud_creds.json')
    #print(buckets = list(storage_client.list_buckets())

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(path_to_file)
    blob.make_public()
    url = blob.public_url
    #returns a public url
    return url

from google.cloud import storage

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )
base_dir = dirname(__file__)
print(base_dir)
download_blob("wordcloud_ftp","72.png",base_dir+"/source/inter/test.png" )

# url = upload_to_bucket("72.png","72.png","wordcloud_ftp")
# print(url)