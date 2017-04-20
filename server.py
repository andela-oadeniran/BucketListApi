import os

from bucketlistapi.app import app

PORT = int(os.getenv('PORT', 5000))


app.run()
