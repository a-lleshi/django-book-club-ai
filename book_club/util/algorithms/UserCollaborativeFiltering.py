"""Recommender using user-based collaborative filtering"""
from surprise import Reader, Dataset, dataset
from surprise import KNNBasic
import heapq
from collections import defaultdict
from operator import itemgetter
from book_club.util.DatasetLoad import *
from book_club import models
from django.core.exceptions import ObjectDoesNotExist
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
                    'user_based': True
                    }

    model = KNNBasic(sim_options=sim_options)
    model.fit(train_set)
    sims_matrix = model.compute_similarities()

    # Get top N similar clubs to the given club
    test_club_inner_id = train_set.to_inner_uid(club_id)
    similarity_row = sims_matrix[test_club_inner_id]

    similar_clubs = []
    for inner_id, score in enumerate(similarity_row):
        if (inner_id != test_club_inner_id):
            similar_clubs.append( (inner_id, score) )

    k_neighbors = heapq.nlargest(k, similar_clubs, key=lambda t: t[1])

    # Get the books they rated, and add up ratings for each item, weighted by club similarity
    candidates = defaultdict(float)
    for similar_club in k_neighbors:
        inner_id = similar_club[0]
        club_sim_score = similar_club[1]
        ratings = train_set.ur[inner_id]
        for rating in ratings:
                candidates[rating[0]] += (rating[1] / 10.0) * club_sim_score

    # Build a dictionary of books the club has already read
    books_read = {}
    for item_id, rating in train_set.ur[test_club_inner_id]:
        books_read[item_id] = 1

    # Get top-rated items from similar clubs
    i = 0
    recommended_books = []
    for item_id, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
        if not item_id in books_read:
            book_id = train_set.to_raw_iid(item_id)
            try:
                book = models.Book.objects.get(ISBN=book_id)
                match = get_match(rating_sum*10)
                recommended_books.append(book)
                i += 1
            except ObjectDoesNotExist:
                pass
            if i > 9:
                break

    return recommended_books
