from app import service
from seed import populate_movies_from_api

if __name__ == '__main__':
    populate_movies_from_api()
    service.run()
