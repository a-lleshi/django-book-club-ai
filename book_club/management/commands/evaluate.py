from django.core.management.base import BaseCommand
from book_club.util.DatasetLoad import *

from surprise import SVD, KNNBasic, NormalPredictor
from book_club.util.Evaluator import Evaluator
from book_club.util.algorithms.ContentKNNAlgo import ContentKNNAlgo


class Command(BaseCommand):
    def handle(self, *args, **options):

     data = get_clubs_ratings_df()
     evaluator = Evaluator(data)

     SVDAlgorithm = SVD(random_state=10)
     evaluator.AddAlgorithm(SVDAlgorithm, "SVD")

     contentKNN = ContentKNNAlgo()
     evaluator.AddAlgorithm(contentKNN, "ContentKNN")

     userKNN = KNNBasic(sim_options={'name':'cosine', 'user_based':True})
     evaluator.AddAlgorithm(userKNN, "UserKNN")

     itemKNN = KNNBasic(sim_options={'name':'cosine', 'user_based':False})
     evaluator.AddAlgorithm(itemKNN, "ItemKNN")

     evaluator.Evaluate(True)
