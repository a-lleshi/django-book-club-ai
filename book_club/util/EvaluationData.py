from surprise.model_selection import train_test_split
from surprise.model_selection import LeaveOneOut
from surprise import KNNBaseline
from surprise import Reader, Dataset, dataset

class EvaluationData:
    """ Evaluate a specific recommendation list with respect to a specific user """

    def __init__(self, df):

        reader = Reader(rating_scale=(1, 10))

        class MyDataset(dataset.DatasetAutoFolds):
            def __init__(self, df, reader):
                self.raw_ratings = [(uid, iid, r, None) for (uid, iid, r) in
                      zip(df['userid'], df['isbn'], df['bookrating'])]
                self.reader = reader

        # Load the data into a 'Dataset' object directly from the pandas df.
        # Note: The fields must be in the order: user, item, rating
        data = MyDataset(df, reader)

        #Build a full training set for evaluating overall properties
        self.fullTrainSet = data.build_full_trainset()
        self.fullAntiTestSet = self.fullTrainSet.build_anti_testset()

        #Build a 80/20 train/test split for measuring accuracy
        self.trainSet, self.testSet = train_test_split(data, test_size=.20, random_state=1)

        #Build a "leave one out" train/test split for evaluating top-N recommenders
        #And build an anti-test-set for building predictions
        LOOCV = LeaveOneOut(n_splits=1, random_state=1)
        for train, test in LOOCV.split(data):
            self.LOOCVTrain = train
            self.LOOCVTest = test

        self.LOOCVAntiTestSet = self.LOOCVTrain.build_anti_testset()

        # # #Compute similarty matrix between items so we can measure diversity
        # sim_options = {'name': 'cosine', 'user_based': False}
        # self.simsAlgo = KNNBaseline(sim_options=sim_options)
        # self.simsAlgo.fit(self.fullTrainSet)


    def GetFullTrainSet(self):
        """ return the full trainset """
        return self.fullTrainSet

    def GetFullAntiTestSet(self):
        """ return the full anti-testset """
        return self.fullAntiTestSet

    def GetAntiTestSetForUser(self, testSubject):
        """ return the anti-testset for a given user """
        trainset = self.trainSet
        fill = trainset.global_mean
        anti_testset = []
        u = trainset.to_inner_uid(int(testSubject))
        user_items = set([j for (j, _) in trainset.ur[u]])
        anti_testset += [(trainset.to_raw_uid(u), trainset.to_raw_iid(i), fill) for
                                 i in trainset.all_items() if
                                 i not in user_items]
        return anti_testset

    def GetTrainSet(self):
        return self.trainSet

    def GetTestSet(self):
        return self.testSet

    def GetLOOCVTrainSet(self):
        return self.LOOCVTrain

    def GetLOOCVTestSet(self):
        return self.LOOCVTest

    def GetLOOCVAntiTestSet(self):
        return self.LOOCVAntiTestSet

    def GetSimilarities(self):
        return self.simsAlgo
