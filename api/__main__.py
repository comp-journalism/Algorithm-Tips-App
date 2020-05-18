import os
from api.api import app

app.run(debug='DEV' in os.environ, port=8080, host='0.0.0.0')
