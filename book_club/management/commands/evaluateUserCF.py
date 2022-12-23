from django.core.management.base import BaseCommand
from book_club.util.DatasetLoad import *
from surprise import KNNBasic
import heapq
from collections import defaultdict
from operator import itemgetter
from surprise.model_selection import LeaveOneOut
from book_club.util.RecommenderMetrics import RecommenderMetrics
from book_club.util.EvaluationData import EvaluationData

class Command(BaseCommand):
    def handle(self, *args, **options):

     data = get_clubs_ratings_df()
     eval_data = EvaluationData(data)

     # Train on leave-One-Out train set
     train_set = eval_data.GetLOOCVTrainSet()
     sim_options = {'name': 'cosine',
                    'user_based': True
                    }

     model = KNNBasic(sim_options=sim_options)
     model.fit(train_set)
     sims_matrix = model.compute_similarities()

     left_out_test_set = eval_data.GetLOOCVTestSet()

     top_n = defaultdict(list)
     k = 10
     for uiid in range(train_set.n_users):
         # Get top N similar clubs to this one
         similarity_row = sims_matrix[uiid]

         similar_clubs = []
         for inner_id, score in enumerate(similarity_row):
             if (inner_id != uiid):
                 similar_clubs.append((inner_id, score))

         k_neighbors = heapq.nlargest(k, similar_clubs, key=lambda t: t[1])

         # Get the books rated and add up ratings for each item, weighted by club similarity
         candidates = defaultdict(float)
         for similar_club in k_neighbors:
             inner_id = similar_club[0]
             sim_score = similar_club[1]
             ratings = train_set.ur[inner_id]
             for rating in ratings:
                 candidates[rating[0]] += (rating[1] / 10) * sim_score

         # Build a dictionary of books the club has already read
         read = {}
         for item_id, rating in train_set.ur[uiid]:
             read[item_id] = 1

         # Get top-rated items from similar clubs:
         i = 0
         for item_id, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
             if not item_id in read:
                 book_id = train_set.to_raw_iid(item_id)
                 top_n[int(train_set.to_raw_uid(uiid))].append( (str(book_id), rating_sum) )
                 i += 1
                 if (i > 40):
                     break

     print("Hit Rate: ", RecommenderMetrics.HitRate(top_n, left_out_test_set))
