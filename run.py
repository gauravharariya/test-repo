# import the creation app application factory
# testing codacy
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
