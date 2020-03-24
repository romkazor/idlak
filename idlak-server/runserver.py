import os
from app import create_app

cdir = os.path.split(os.path.abspath(__file__))[0]

config_fn = os.path.join(cdir, 'config.ini')

app = create_app(config_fn)

if __name__ == '__main__':
    app.run(host=app.config["HOST"], port=app.config["PORT"])
