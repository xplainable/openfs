# featurestore
An S3 feature store client for data pipelines

# Quick Start
## Creating a Store
``` python
import featurestore as fs
from featurestore.stores import BoosterStore
from featurestore.boosters import Booster
import os

# <- import files to upload here

# Connect to store bucket
fs.client.connect(
    region_name=os.environ['FSTORE_REGION'],
    endpoint_url=os.environ['FSTORE_ENDPOINT_URL'],
    access_key_id=os.environ['FSTORE_ACCESS_KEY'],
    secret_access_key=os.environ['FSTORE_SECRET_KEY']
)

# Create store
store = BoosterStore("store_name", "description of store", "some_primary_key")

# Upload store
response = store.upload(files, filenames)
```

## Creating a Booster Dataset
``` python
# Create booster
booster = Booster(
    name="booster_name",
    description="booster description",
    store_id=response['store_id'])

# Add features
booster.add_single("feature_1", alias="alias_for_feature")
booster.add_group(["feature_2", "feature_3"], alias="grouped_feature", how='sum')

# pull features from store (for testing)
df = booster.create_df()

# upload booster
booster.upload()
```

## Viewing Stores

```python
fb.client.list_stores()
```