from book_club.util.EvaluationData import EvaluationData
from book_club.util.EvaluatedAlgo import EvaluatedAlgo
from book_club import models
from django.core.exceptions import ObjectDoesNotExist

class Evaluator:
    """ Returns the "Algorithm", "RMSE", "MAE", "HR", "cHR", "ARHR", "Coverage", using the specified recommender algorithm for the books. """

    algorithms = []

    def __init__(self, dataset):
        ed = EvaluationData(dataset)
        self.dataset = ed

    def AddAlgorithm(self, algorithm, name):
        alg = EvaluatedAlgo(algorithm, name)
        self.algorithms.append(alg)

    def Evaluate(self, doTopN):
        results = {}
        for algorithm in self.algorithms:
            print("Evaluating ", algorithm.GetName(), "...")
            results[algorithm.GetName()] = algorithm.Evaluate(self.dataset, doTopN)

        # Print results
        print("\n")

        if (doTopN):
            print("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
                    "Algorithm", "RMSE", "MAE", "HR", "cHR", "ARHR", "Coverage"))
            for (name, metrics) in results.items():
                print("{:<10} {:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f}".format(
                        name, metrics["RMSE"], metrics["MAE"], metrics["HR"], metrics["cHR"], metrics["ARHR"],
                                      metrics["Coverage"]))
        else:
            print("{:<10} {:<10} {:<10}".format("Algorithm", "RMSE", "MAE"))
            for (name, metrics) in results.items():
                print("{:<10} {:<10.4f} {:<10.4f}".format(name, metrics["RMSE"], metrics["MAE"]))

        print("\nLegend:\n")
        print("RMSE: Root Mean Squared Error - lower values mean better accuracy")
        print("MAE: Mean Absolute Error - lower values mean better accuracy")
        print("HR: Hit Rate - how often we are able to recommend a left-out rating; higher values are better")
        print("cHR: Cumulative Hit Rate - hit rate, confined to ratings above a certain threshold; higher values are better")
        print("ARHR: Average Reciprocal Hit Rank - hit rate that takes the ranking into account; higher values are better" )
        print("Coverage: ratio of users for whom recommendations above a certain threshold exist; higher values are better")
