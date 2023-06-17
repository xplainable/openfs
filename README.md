
<br></br>
<div align="center">
<h1 align="center">openfs</h1>
<h3 align="center">An S3 feature store client for data pipelines.</h3>
    
[![Python](https://img.shields.io/pypi/pyversions/openfs)](https://pypi.org/project/openfs/)
[![PyPi](https://img.shields.io/pypi/v/openfs?color=blue)](https://pypi.org/project/openfs/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/xplainable/openfs/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/openfs)](https://pepy.tech/project/openfs)
    
**Openfs** provides a simple api to boost the quality of your training data
while keeping your data pipelines clean and manageable.
</div>

# Installation
```shell
pip install openfs
```

## Quick Start
### Creating a Store
``` python
import openfs as fs
from openfs.stores import FeatureStore
from openfs.boosters import Booster
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
store = FeatureStore("store_name", "description of store", "some_primary_key")

# Upload store
response = store.upload(files, filenames)
```

### Creating a Booster Dataset
``` python
# Create booster
booster = Booster(store_id=response['store_id'])

# Add features
booster.add_single("feature_1", alias="alias_for_feature")
booster.add_group(["feature_2", "feature_3"], alias="grouped_feature", how='sum')

# pull features from store (for testing)
df = booster.create_df()

# upload booster
booster.upload(name="booster_name", description="booster description")
```

### Viewing Stores

```python
fb.client.list_stores()
```

<br></br>

## Contributors
We'd love to welcome contributors to ``openfs`` to help make training data
richer and more open for everyone. We're working on our contributor docs at the
moment, but if you're interested in contributing, please send us a message at
contact@xplainable.io.


<div align="center">
<br></br>
<br></br>
Thanks for trying openfs!
<br></br>
<strong>Made with ❤️ in Australia</strong>
<br></br>
<hr>
&copy; copyright xplainable pty ltd
</div>

