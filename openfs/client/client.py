from boto3 import session
import json

class Client:

    def __init__(self, store_name='booster-store'):
        self.session = None
        self.client = None
        self.resource = None
        self.store_name = store_name

    def connect(
            self, region_name, endpoint_url, access_key_id, secret_access_key):
        # Initiate session
        self.client = session.Session().client(
            's3',
            region_name=region_name,
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key
            )
        
        self._check_connection()
        
    def _check_connection(self):
        try:
            self.client.list_buckets()
            print('Connection successful.')
        except Exception as e:
            raise SystemExit('Failed to connect: ' + str(e))
        
    def check_instantiated(self):
        if self.client is None:
            raise SystemExit('Client not instantiated.')

    def list_stores(self):
        self.check_instantiated()
        
        # fetch metadata from datastore
        response = self.client.list_objects_v2(Bucket=self.store_name)
        
        if 'Contents' in response:
            datastores = []
            for item in response['Contents']:
                # Extract the directory name
                name = item['Key'].split('/')[-1].split('.')[0]

                if name != 'metadata':
                    continue

                response = self.client.get_object(
                    Bucket=self.store_name,
                    Key=item["Key"])

                # Get the file data from the response
                file_data = response['Body'].read().decode('utf-8')

                # Convert JSON to Python dictionary
                metadata = json.loads(file_data)

                metadata['files'] = len(metadata['files'])

                datastores.append(metadata)
                    
            return datastores
