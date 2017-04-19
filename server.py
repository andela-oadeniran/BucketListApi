import os

from bucketlistapi.utils import app

PORT = int(os.getenv('PORT', 5000))


app.run()
