from surprise import AlgoBase
from surprise import PredictionImpossible
from book_club.util.DatasetLoad import *
import math
import numpy as np
import heapq

class ContentKNNAlgo(AlgoBase):

    def __init__(self, k=40, sim_options={}):
        AlgoBase.__init__(self)
        self.k = k

    def fit(self, trainset):
        """ Fit the model by computing the similarity between items """
        AlgoBase.fit(self, trainset)

        # Compute item similarity matrix based on content attributes

        years = getYears()
        titles = getTitles()

        print("Computing content-based similarity matrix...")

        self.similarities = np.zeros((self.trainset.n_items, self.trainset.n_items))

        for i in range(self.trainset.n_items):
            if (i % 100 == 0):
                print(i, " of ", self.trainset.n_items)
            for j in range(i+1, self.trainset.n_items):
                book_id = str(self.trainset.to_raw_iid(i))
                other_book_id = str(self.trainset.to_raw_iid(j))
                year_similarity = self.compute_year_similarity(book_id, other_book_id, years)
                self.similarities[i, j] = year_similarity
                self.similarities[j, i] = self.similarities[i, j]

        print("...done.")

        return self

    def compute_year_similarity(self, book1, book2, years):
        """ Compute the similarity between two books based on their publication year. """
        diff = abs(years[book1] - years[book2])
        sim = math.exp(-diff / 10.0)
        return sim

    def estimate(self, u, i):
        """ Return the top-k most-similar items to the given item. """
        if not (self.trainset.knows_user(u) and self.trainset.knows_item(i)):
            raise PredictionImpossible('User and/or item is unkown.')

        # Build up similarity scores between this item and everything the user rated
        neighbors = []
        for rating in self.trainset.ur[u]:
            genre_similarity = self.similarities[i,rating[0]]
            neighbors.append( (genre_similarity, rating[1]) )

        # Extract the top-K most-similar ratings
        k_neighbors = heapq.nlargest(self.k, neighbors, key=lambda t: t[0])

        # Compute average sim score of K neighbors weighted by user ratings
        sim_total = weighted_sum = 0
        for (sim_score, rating) in k_neighbors:
            if (sim_score > 0):
                sim_total += sim_score
                weighted_sum += sim_score * rating

        if (sim_total == 0):
            raise PredictionImpossible('No neighbors')

        return weighted_sum / sim_total
