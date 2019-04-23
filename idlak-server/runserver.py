from app import create_app

app = create_app('config.ini')

if __name__ == '__main__':
    app.run()
