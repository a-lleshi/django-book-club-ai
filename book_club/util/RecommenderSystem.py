from surprise import Reader, Dataset
from book_club.util.DatasetLoad import *
from surprise import SVD, model_selection
from collections import defaultdict


""" Recommender System for only one user no longer used however it is kept for reference as a base of the recommender system """

def clubItemRating():
    """ Return a dataframe of club item ratings """
    books_clubs_ratings = get_clubs_ratings_df()
    return books_clubs_ratings

def model_loader():
    """ Load the model for the recommender system """
    club_item_rating = clubItemRating()
    reader = Reader(rating_scale=(1, 10))
    data = Dataset.load_from_df(club_item_rating, reader)

    trainset, testset = model_selection.train_test_split(data, test_size=0.2)

    model = SVD(n_factors=80, lr_all=0.005, reg_all=0.04)
    #model = KNNBasic(sim_options={'name':'cosine', 'user_based':True}, n_factors=80, lr_all=0.005, reg_all=0.04, verbose=True)
    model.fit(trainset) 
    return model.test(testset)

def get_top_n(predictions, n=10):
    """ Get top-N (10 top books) recommendation for each user """
    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n

def get_reading_list(user_id):
    """ Retrieve full book titles from books_clubs_ratings dataframe """
    reading_list = []
    books_clubs_ratings = get_clubs_ratings_df()

    loaded_model = pickle.load(open('finalized_model.sav', 'rb'))

    top_n = get_top_n(loaded_model, n=10)

    # Get the top-N recommendation for a users
    for n in top_n[user_id]:
        book, rating = n
        title = books_clubs_ratings.loc[books_clubs_ratings.isbn==book].booktitle.unique()[0]
        url = books_clubs_ratings.loc[books_clubs_ratings.isbn==book].imageurls.unique()[0]
        book_id = int(books_clubs_ratings.loc[books_clubs_ratings.isbn==book].id.unique()[0])
        reading_list.append((title, rating, url, book_id))

    return reading_list

def save_to_file():
    """ To save the model to a file and load the model from a file to cut down recommendation for a user by half"""
    filename = 'finalized_model.sav'
    model = model_loader()
    pickle.dump(model, open(filename, 'wb'))
