from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Function to get MongoDB connection
def get_db_connection():
    username = os.getenv('MONGO_USERNAME')
    password = os.getenv('MONGO_PASSWORD')
    client = MongoClient(f"mongodb+srv://{username}:{password}@cluster0.71tvv.mongodb.net/")
    return client['formdata']


# Function to retrieve and save files
def retrieve_files(document_id, output_directory):
    db = get_db_connection()
    collection = db['education_background']

    # Fetch the document by its ID
    document = collection.find_one({'_id': ObjectId(document_id)})

    if document and 'files' in document:
        os.makedirs(output_directory, exist_ok=True)

        # Iterate over the files and save them to the output directory
        for i, file_data in enumerate(document['files']):
            filename = file_data['filename']
            filepath = os.path.join(output_directory, filename)
            with open(filepath, 'wb') as file:
                file.write(file_data['data'])
            print(f"Saved {filename} to {filepath}")
    else:
        print("No files found for this document.")


if __name__ == "__main__":
    # Example usage
    document_id = input("Enter the MongoDB document ID: ")
    output_directory = "retrieved_files"  # Directory where files will be saved
    retrieve_files(document_id, output_directory)
