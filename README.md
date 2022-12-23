# Book club AI Recommender System.

This is a project in year 2 computer science, where we produced a book club website where users can sign up, log in, register book clubs, join and leave book clubs.

These book clubs each had a book that the club was currectly reading and each cycle once the book is finished the members of the club can rate the books.

This then allows a random selection of a member to be able to then pick the next book using an AI Recommender System.

## Contents on this page:
- [Project Deployment](#Project-deployment)
- [Project Structure](#Project-structure)
- [Intallation instructions](#Installation-instructions)
- [Sources used for webapp](#Sources)

## Project deployment 
This project is deployed on heruko servers and using a postgres database.

**WARNING**: Due to Heurok free deployment the RAM limitations could sometimes not handle the recommendation system; therefore would take some page refresing until it works.

**UPDATE**: Heruko no longer offers free tier :/

## Project structure
The project is called `system`.  It currently consists of a single app `book_club`. With the recommender system within a folder named `util` within the `book_club` app.

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:
```
$ python3 manage.py migrate --run-syncdb
```

Add cache to the database:
```
$ python3 manage.py createcachetable
```

Seed the development database with (due to seeding from CSVs will take around 5-7 minutes to seed):

```
$ python3 manage.py seed
```

Before running tests you must run the following commands:

```
$ python3 manage.py collectstatic
```

Run all tests with:
```
$ python3 manage.py test
```

Run the server with the following command:
```
$ python3 manage.py runserver
```


## Sources

- All code has borrowed ideas from the clucker training videos.
- [Django filter](https://django-filter.readthedocs.io/en/stable/index.html) was used to inspire the use of filters (see book_club.filters.py) for models within the Django application.
- [AI Recommender System Training](https://www.linkedin.com/learning/building-recommender-systems-with-machine-learning-and-ai/recommender-engine-walkthrough-part-1)
