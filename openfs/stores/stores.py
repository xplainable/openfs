from openfs import client
import json
import os
from datetime import datetime
from io import StringIO
import uuid

class FeatureStore:

    def __init__(self, name, description, primary_key):
        self.name = name
        self.description = description
        self.primary_key = primary_key

        self.uploaded_files = []
        self.booster_metadata = self._gen_booster_metadata()
        

    def _check_primary_key(self, df):
        if self.primary_key not in df.columns:
            raise ValueError(
                f"Primary key {self.primary_key} not found in dataframe.")

    def _local_file_store(self, file, id):
        # upload file to datastore

        path = f"datastore/{self.booster_metadata['id']}"

        if not os.path.exists(path):
            os.makedirs(path)

        filename = f"{path}/{id}.csv"
        file.to_csv(filename)

    def _local_metadata_store(self, file):
        # upload file to datastore
        with open(f"datastore/{file['id']}/metadata.json", "w") as f:
            json.dump(file, f)

    def _upload_file(self, file, id):
        
        client.check_instantiated()

        path = f"datastore/{self.booster_metadata['id']}"
        filename = f"{id}.csv"

        csv_buffer = StringIO()
        file.to_csv(csv_buffer)

        try:
            client.client.put_object(Bucket=client.store_name, 
                    Key=f'{path}/{filename}', 
                    Body=csv_buffer.getvalue()
                    )

        except Exception as e:
            print(e)

    def _upload_metadata(self, file):

        client.check_instantiated()

        json_buffer = StringIO()
        json.dump(file, json_buffer)
        json_buffer.seek(0)

        path = f"datastore/{self.booster_metadata['id']}"
        filename = f"metadata.json"
        try:
            client.client.put_object(Bucket=client.store_name, 
                    Key=f'{path}/{filename}', 
                    Body=json_buffer.getvalue().encode()
                    )

        except Exception as e:
            print(e)

    def _gen_booster_metadata(self):
        metadata = {
            "id": str(uuid.uuid4()),
            "name": self.name,
            "description": self.description,
            "primary_key": self.primary_key,
            "files": self.uploaded_files
        }

        return metadata

    def _gen_file_metadata(self, file, filename):
        dtypes = {i: str(v) for i, v in dict(file.dtypes).items()}
        metadata = {
            "id": str(uuid.uuid4()),
            "created": str(datetime.utcnow()),
            "filename": filename,
            "nrows": file.shape[0],
            "ncols": file.shape[1],
            "dtypes": dtypes
        }

        return metadata

    def upload(self, files, filenames=None):

        for file in files:
            self._check_primary_key(file)

        if filenames is None:
            filenames = [f"file_{i}" for i in range(len(files))]

        for file, filename in zip(files, filenames):
            metadata = self._gen_file_metadata(file, filename)
            self._upload_file(file, metadata["id"])
            self.uploaded_files.append(metadata)

        self.booster_metadata["created"] = str(datetime.utcnow())
        self._upload_metadata(self.booster_metadata)

        return {
                "message": "success",
                "store_id": self.booster_metadata['id']
                }
    