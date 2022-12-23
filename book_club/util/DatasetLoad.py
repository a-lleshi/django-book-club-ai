from unittest import skip
import pandas as pd
import numpy as np
import pickle
from surprise import Dataset
from book_club import models
from collections import defaultdict
import random

""" Load the dataset from db and return a pandas dataframe """

def loadBooksData():
    """ Import the books data from db and return a pandas dataframe """
    books = models.Book.objects.all()

    df = pd.DataFrame(list(books.values()))
    return df

def loadUsersData():
    """ Import the users data from db and return a pandas dataframe """
    users = models.User.objects.all()

    df = pd.DataFrame(list(users.values()))
    return df

def loadUserRatingsData():
    """ Import the users rating data from db and return a pandas dataframe """
    ratings = models.UserRating.objects.all()
    df = pd.DataFrame(list(ratings.values()))
    return df

""" Cleaning up the data """

def bookDataClean():
    """ Clean up the books data """
    books = loadBooksData()

    books.columns = books.columns.str.strip().str.lower().str.replace('-', '_')
    books.rename(columns={'imageurl': 'url'}, inplace=True)
    books.drop(columns=['imageurlm', 'imageurll'], inplace=True)
    books.yearofpublication = pd.to_numeric(books.yearofpublication, errors='coerce')

    # Replace all years of zero with NaN
    books.yearofpublication.replace(0, np.nan, inplace=True)

    books_from_the_future = books[books.yearofpublication>2022] 

    books = books.loc[~(books.isbn.isin(books_from_the_future.isbn))]

    books.publisher = books.publisher.str.replace('&amp', '&', regex=False)

    return books

def userDataClean():
    """ Clean up the users data """
    users = loadUsersData()
    users.columns = users.columns.str.strip().str.lower().str.replace('-', '_')

    # Drop sensitive data
    users.drop(columns=['password', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'personal_statement'], inplace=True)

    # A sensible cutoff for the age of users
    users.loc[(users.age<10) | (users.age>100), 'age'] = np.nan

    # Split location into city, state and country
    user_location_expanded = users.location.str.split(',', 2, expand=True)
    user_location_expanded.columns = ['city', 'state', 'country']
    users = users.join(user_location_expanded)
    users.drop(columns=['location'], inplace=True)
    users.country.replace('', np.nan, inplace=True)

    return users

def ratingDataClean():
    """ Clean up the user ratings data """
    ratings = loadUserRatingsData()
    ratings.columns = ratings.columns.str.strip().str.lower().str.replace('-', '_')

    # Books with ratings 0 removed
    ratings = ratings[ratings.bookrating != 0]

    return ratings

def joinBooksRatings():
    """ Join the books and ratings data """

    # Load clean book and ratings data
    books = bookDataClean()
    ratings = ratingDataClean()

    # Join the books and ratings data
    books_with_ratings = ratings.join(books.set_index('isbn'), on='isbn', lsuffix = '_left')
    books_with_ratings.dropna(subset=['booktitle'], inplace=True)

    return books_with_ratings

def dictOfMultipleISBN():
    """ Ran once to get unique ISBN numbers for each book """
    books_with_ratings = joinBooksRatings()

    multiple_isbns = books_with_ratings.groupby('booktitle').isbn.nunique()
    multiple_isbns.value_counts()

    has_mult_isbns = multiple_isbns.where(multiple_isbns>1)
    has_mult_isbns.dropna(inplace=True) # remove NaNs, which in this case is books with a single ISBN number

    # Create dictionary for books with multiple isbns
    def make_isbn_dict(df):
        count = 0
        title_isbn_dict = {}
        for title in has_mult_isbns.index:
            print(f'Multiple isbn {count}', end='\r')
            isbn_series = df.loc[df.booktitle==title].isbn.unique()
            title_isbn_dict[title] = isbn_series.tolist()
            count += 1

        return title_isbn_dict

    dict_unique_isbn = make_isbn_dict(books_with_ratings)

    # As the loop takes a while to run (8 min on the full dataset), pickle this dict for future use
    with open('multiple_isbn_dict.pickle', 'wb') as handle:
        pickle.dump(dict_unique_isbn, handle, protocol=pickle.HIGHEST_PROTOCOL)

def addUniqueISBN(df):
    """ Add unique ISBN number for each book """
    multiple_isbn_dict = pickle.load(open('multiple_isbn_dict.pickle', 'rb'))

    df['unique_isbn'] = df.apply(lambda row: multiple_isbn_dict[row.booktitle][0] if row.booktitle in multiple_isbn_dict.keys() else row.isbn, axis=1)
    return df

def booksWithRatings():
    books_with_ratings = addUniqueISBN(joinBooksRatings())

    return books_with_ratings

def joinUsersBooksRatings():
    """ Join the users and booksRatings data """
    users = userDataClean()
    books_with_ratings = booksWithRatings()

    books_users_ratings = books_with_ratings.join(users.set_index('id'), on='userid')

    return books_users_ratings

def getYears():
    """ Get the years of publication for each book """
    years = defaultdict(int)
    books = models.Book.objects.all()
    for book in books:
        year = book.YearOfPublication
        id = book.id
    return years

def getTitles():
    """ Get the titles of each book """
    titles = defaultdict(int)
    books = models.Book.objects.all()
    for book in books:
        title = book.BookTitle
        id = book.id
        titles[id] = title
    return titles

def getTopPopularBooks(n=10):
    """ Get the top n (10) popular books """
    bookPopularities = defaultdict(int)
    ratings = defaultdict(int)
    booksDf = addUniqueISBN(bookDataClean())
    booksDf.drop(columns=['isbn', 'booktitle', 'bookauthor', 'yearofpublication',
       'publisher', 'imageurls'], inplace=True)
    books = booksDf.values.tolist()
    for index, book in books:
        ratings[book] += 1
    p = 1
    for book, ratingCount in sorted(ratings.items(), key=lambda x:x[1], reverse=True):
        bookPopularities[book] = p
        p += 1

    topBooks = []
    bookList = list(bookPopularities.keys())
    for isbn in bookList[:10]:
        book = models.Book.objects.filter(ISBN=isbn)[0]
        topBooks.append((book, random.randint(90,99)))
        topBooks.sort(key=lambda x: x[1], reverse=True)

    return topBooks

def get_clubs_ratings_df():
    """ Return the dataframe of ratings for each book club """
    ratings = get_club_book_ratings()
    df = pd.DataFrame(ratings, columns=['userid', 'isbn', 'bookrating'])
    return df

def get_club_book_ratings():
    """ Get the ratings for each book in each club """
    clubs_books_ratings = []
    clubs = models.Club.objects.all()
    memberships = models.Membership.objects.all()
    allRatings = booksWithRatings()
    allRatings.drop(columns=['isbn','id', 'booktitle','bookauthor', 'yearofpublication',
    'publisher', 'imageurls',], inplace=True)
    ratings = allRatings.values.tolist()

    for club in clubs:
        club_users = memberships.filter(club=club)

        # Get a set of all books read by the users of that club
        rated_books = {}
        for membership in club_users:
            user = membership.user
            rated_books_by_user = []
            for id, userid, rating, isbn in ratings:
                if userid == user.id:
                      rated_books_by_user.append((isbn, rating))
            for isbn, rating in rated_books_by_user:
                if rated_books.get(isbn) is not None:
                    pair = rated_books.get(isbn)
                    pair[0] += rating
                    pair[1] += 1
                    rated_books[isbn] = pair
                else:
                    pair = [rating, 1]
                    rated_books[isbn] = pair

        # Iterate through the book set and get all ratings
        for bookISBN in rated_books.keys():
            pair = rated_books.get(bookISBN)
            avg_rating = pair[0] / pair[1]
            clubs_books_ratings.append((club.id, bookISBN, avg_rating))
    return clubs_books_ratings
