import itertools
from surprise import accuracy
from collections import defaultdict

class RecommenderMetrics:

    def MAE(predictions):
        """ Returns the mean absolute error of the predictions. """
        return accuracy.mae(predictions, verbose=False)

    def RMSE(predictions):
        """ Returns the root mean squared error of the predictions. """
        return accuracy.rmse(predictions, verbose=False)

    def GetTopN(predictions, n=20, minimumRating=6.0):
        """ Get top-N recommendation for each user from a set of predictions. """
        topN = defaultdict(list)

        for userId, bookId, actualRating, estimatedRating, _ in predictions:
            if estimatedRating >= minimumRating:
                topN[int(userId)].append((bookId, estimatedRating))

        for userId, ratings in topN.items():
            ratings.sort(key=lambda x:x[1], reverse=True)
            topN[int(userId)] = ratings[:n]

        return topN

    def HitRate(topNPredicted, leftOutPredictions):
        """ Compute the hit-rate of the model on the left-out set. """
        hits = total = 0

        for leftOut in leftOutPredictions:
            userId = leftOut[0]
            leftOutBookId = leftOut[1]
            hit = False
            for bookId, predictedRating in topNPredicted[int(userId)]:
                if leftOutBookId == bookId:
                    hit = True
                    break
            if hit:
                hits += 1
            total += 1

        return hits / total

    def CumulativeHitRate(topNPredicted, leftOutPredictions, ratingCutoff=0):
        """ Cumulative hit rate for set of predictions at a particular cutoff point. """
        hits = total = 0

        for userId, leftOutBookId, actualRating, estimatedRating, _ in leftOutPredictions:
            if actualRating >= ratingCutoff:
                hit = False
                for bookId, predictedRating in topNPredicted[int(userId)]:
                    hit = True
                    break
            if hit:
                hits += 1
            total += 1

        return hits / total

    def RatingHitRate(topNPredicted, leftOutPredictions):
        """ Compute the hit-rate of the model on the left-out set. """
        hits = defaultdict(float)
        total = defaultdict(float)

        for userId, leftOutBookId, actualRating, estimatedRating, _ in leftOutPredictions:
                hit = False
                for bookId, predictedRating in topNPredicted[int(userId)]:
                    if int(leftOutBookId) == bookId:
                        hit = True
                        break
                if hit:
                        hits[actualRating] += 1
                total[actualRating] += 1

        for rating in sorted(hits.keys()):
            print( rating, hits[rating] / total[rating])

    def AverageReciprocalHitRank(topNPredicted, leftOutPredictions):
        """ Computes the average reciprocal hit rank of the predicted ratings. """
        sum = total = 0

        for userId, leftOutBookId, actualRating, estimatedRating, _ in leftOutPredictions:
            hitRank = 0
            rank = 0
            for bookId, predictedRating in topNPredicted[int(userId)]:
                rank += 1
                if leftOutBookId == bookId:
                    hitRank = rank
                    break
            if hitRank > 0:
                sum += 1.0 / hitRank

            total += 1

        return sum / total

    def UserCoverage(topNPredicted, numUsers, ratingThreshold=0):
        """ Compute the average coverage of the predicted rating of the test set by the top-N list. """
        hits = 0
        for userId in topNPredicted.keys():
            hit = False
            for bookId, predictedRating in topNPredicted[userId]:
                if predictedRating >= ratingThreshold:
                    hit = True
                    break
            if hit:
                hits += 1
        return hits / numUsers

    def Diversity(topNPredicted, simsAlgo):
        """ Average popularity rank of books recommended for each user. """
        n = total = 0
        simMatrix = simsAlgo.compute_similarities()
        for userId in topNPredicted.keys():
            pairs = itertools.combinations(topNPredicted[userId], 2)
            for pair in pairs:
                book1 = pair[0][0]
                book2 = pair[1][1]
                innerId1 = simsAlgo.trainset.to_inner_iid(int(book1))
                innerId2 = simsAlgo.trainset.to_inner_iid(int(book2))
                similarity = simMatrix[innerId1][innerId2]
                total += similarity
                n += 1
        return 1 - (total / n)

    def Novelty(topNPredicted, rankings):
        """ Average popularity rank of books recommended for each user. """
        n = total = 0
        for userId in topNPredicted.keys():
            for rating in topNPredicted[userId]:
                bookId = rating[0]
                rank = rankings[bookId]
                total += rank
                n += 1
        return total / n
