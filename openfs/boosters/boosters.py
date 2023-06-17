from openfs import client
import json
import os
import uuid
from io import StringIO
import pandas as pd


class Booster:

    def __init__(self, store_id, booster_id=None):
        self.store_id = store_id
        self.features = []
        self.aliases = []
        self.metadata = self._fetch_meta()
        self.booster_id = self._load_booster(booster_id)
        self.name = None
        self.description = None

    def _fetch_local_meta(self):
        # fetch metadata from datastore
        with open(f"datastore/{self.store_id}/metadata.json", "r") as f:
            metadata = json.load(f)

        return metadata
    
    def _fetch_meta(self):

        try:
            # fetch metadata from datastore
            response = client.client.get_object(
                Bucket=client.store_name,
                Key=f'datastore/{self.store_id}/metadata.json'
                )

            file_content = response['Body'].read().decode('utf-8')
            return json.loads(file_content)

        except Exception as e:
            raise SystemExit("Could not find metadata")
        
    def _load_local_booster(self, booster_id):
        if booster_id is None:
            return None
        
        if booster_id not in [i.split(".")[0] for i in os.listdir(
            f"datastore/{self.store_id}/boosters/")]:

            raise ValueError(f"Booster {booster_id} not found.")

        path = f"datastore/{self.store_id}/boosters/{booster_id}.json"
        with open(path, "r") as f:
            self.features = json.load(f)
            self.aliases = [i["alias"] for i in self.features]

        return booster_id
    
    def _load_booster(self, booster_id):
        if booster_id is None:
            return None
        
        try:
            # fetch metadata from datastore
            response = client.client.get_object(
                Bucket=client.store_name,
                Key=f'datastore/{self.store_id}/boosters/{booster_id}.json'
                )
            
            file_content = response['Body'].read().decode('utf-8')
            booster_data = json.loads(file_content)

            self.features = booster_data['features']
            self.name = booster_data['name']
            self.description = booster_data['description']
            self.aliases = [i["alias"] for i in self.features]

            return booster_id

        except Exception as e:
            raise SystemExit(f"Could not find booster {booster_id}")
    
    def _verify(self, feature_name, alias, file_id):
        if file_id not in [i["id"] for i in self.metadata["files"]]:
            raise ValueError(f"File {file_id} not found.")
        
        columns = [i for i in self.metadata["files"] if \
                   i["id"] == file_id][0]["dtypes"].keys()
        
        if feature_name not in columns:
            raise ValueError(
                f"Feature {feature_name} not found in file {file_id}.")
        
        if alias in self.aliases:
            raise ValueError(f"Alias {alias} already exists.")
    
    def add_single(self, feature_name, alias=None, file_id=None):

        if alias is None:
            alias = feature_name

        if file_id is None:
            for file in self.metadata["files"]:
                if feature_name in file["dtypes"].keys():
                    file_id = file["id"]
                    break
        
        self._verify(feature_name, alias, file_id)

        item = {
            "file_id": file_id,
            "type": "single",
            "name": feature_name,
            "alias": alias,
        }

        if item in self.features:
            raise ValueError(f"Feature {feature_name} already exists.")
        
        self.features.append(item)
        self.aliases.append(alias)

    def add_group(self, feature_names, alias, file_id=None, how="sum"):
            
            if file_id is None:
                for file in self.metadata["files"]:
                    if feature_names[0] in file["dtypes"].keys():
                        file_id = file["id"]
                        break
            
            for feature_name in feature_names:
                self._verify(feature_name, alias, file_id)
    
            item = {
                "file_id": file_id,
                "type": "group",
                "names": feature_names,
                "alias": alias,
                "how": how
            }
    
            if item in self.features:
                raise ValueError(f"Feature group already exists.")
            
            self.features.append(item)
            self.aliases.append(alias)


    def _local_booster_store(self):
        _id = str(uuid.uuid4())
        path = f"datastore/{self.store_id}/boosters"
        if not os.path.exists(path):
            os.makedirs(path)

        with open(f"{path}/{_id}.json", "w") as f:
            json.dump(self.features, f)

    def upload(self, name: str, description: str):
        self.name = name
        self.description = description

        try:
            _id = str(uuid.uuid4())
            path = f"datastore/{self.store_id}/boosters"

            body = {
                "booster_id": _id,
                "store_id": self.store_id,
                "name": self.name,
                "description": self.description,
                "features": self.features
            }

            client.client.put_object(
                Bucket=client.store_name,
                Key=f'{path}/{_id}.json',
                Body=json.dumps(body)
            )

            return {
                "message": "success",
                "booster_id": _id
                }
        
        except Exception as e:
            raise SystemExit(f"Could not upload booster {self.booster_id}")

    def _load_local_features(self):
        for feature in self.features:
            if feature["type"] == "single":
                file = [i for i in self.metadata["files"] if \
                        i["id"] == feature["file_id"]][0]
                
                df = pd.read_csv(f"datastore/{self.store_id}/{file['id']}.csv")
                ser = df[feature["name"]]

                df_out = pd.DataFrame({
                    self.metadata["primary_key"]: df[self.metadata["primary_key"]],
                    feature["alias"]: ser})

                yield df_out

            elif feature["type"] == "group":
                file = [i for i in self.metadata["files"] if \
                        i["id"] == feature["file_id"]][0]
                
                df = pd.read_csv(f"datastore/{self.store_id}/{file['id']}.csv")
                ser = df[feature["names"]].sum(axis=1)
                
                df_out = pd.DataFrame({
                    self.metadata["primary_key"]: df[self.metadata["primary_key"]],
                    feature["alias"]: ser})

                yield df_out

    def _load_csv(self, file_id):
        response = client.client.get_object(
            Bucket=client.store_name,
            Key=f'datastore/{self.store_id}/{file_id}.csv'
            )
        
        file_content = response['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(file_content))
        return df

    def _load_features(self):
        for feature in self.features:
            if feature["type"] == "single":
                file = [i for i in self.metadata["files"] if \
                        i["id"] == feature["file_id"]][0]
                
                df = self._load_csv(file['id'])
                ser = df[feature["name"]]

                df_out = pd.DataFrame({
                    self.metadata["primary_key"]: df[self.metadata["primary_key"]],
                    feature["alias"]: ser})

                yield df_out

            elif feature["type"] == "group":
                file = [i for i in self.metadata["files"] if \
                        i["id"] == feature["file_id"]][0]
                
                df = self._load_csv(file['id'])

                ser = df[feature["names"]].sum(axis=1)
                
                df_out = pd.DataFrame({
                    self.metadata["primary_key"]: df[self.metadata["primary_key"]],
                    feature["alias"]: ser})

                yield df_out

    def create_df(self):
        # join all features on primary key
        df = None
        for _idx, _df in enumerate([i for i in self._load_features()]):
            if _idx > 0:
                df = df.merge(_df, on=self.metadata["primary_key"], how="outer")
            else:
                df = _df
        
        return df
