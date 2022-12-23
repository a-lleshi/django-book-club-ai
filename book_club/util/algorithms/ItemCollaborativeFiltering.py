"""Recommender using item-based collaborative filtering"""
from surprise import Reader, Dataset, dataset
from surprise import KNNBasic
import heapq
from collections import defaultdict
from operator import itemgetter
from book_club.util.DatasetLoad import *
import random


def getTopNRecs(club_id, k=10):
    """ Return the top-N recommendation for club_id """ 

    reader = Reader(rating_scale=(1, 10))
    df = get_clubs_ratings_df()

    class MyDataset(dataset.DatasetAutoFolds):
        def __init__(self, df, reader):
            self.raw_ratings = [(uid, iid, r, None) for (uid, iid, r) in
                    zip(df['userid'], df['isbn'], df['bookrating'])]
            self.reader = reader

    data = MyDataset(df, reader)
    train_set = data.build_full_trainset()

    sim_options = {'name': 'cosine',
            'user_based': False
            }
    model = KNNBasic(sim_options=sim_options)
    model.fit(train_set)
    sims_matrix = model.compute_similarities()

    test_club_inner_id = train_set.to_inner_uid(club_id)

    # Get the top K items rated
    test_club_ratings = train_set.ur[test_club_inner_id]
    k_neighbors = heapq.nlargest(k, test_club_ratings, key=lambda t: t[1])

    # Get similar items to books that were liked (weighted by rating)
    candidates = defaultdict(float)
    for item_id, rating in k_neighbors:
        similarity_row = sims_matrix[item_id]
        for inner_id, score in enumerate(similarity_row):
            candidates[inner_id] += score * (rating / 10)

    # Build a dictionary of book the club has already read
    read = {}
    for item_id, rating in train_set.ur[test_club_inner_id]:
            read[item_id] = 1

    # Get top-rated boks from similar clubs:
    i = 0
    recommended_books = []
    for item_id, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
        if not item_id in read:
            book_id = train_set.to_raw_iid(item_id)
            recommended_books.append(book_id)
            i += 1
            if i > 9:
                break
    return recommended_books
