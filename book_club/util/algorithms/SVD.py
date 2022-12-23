from surprise import SVD
from book_club import models
from django.core.exceptions import ObjectDoesNotExist
from surprise import Reader, Dataset, dataset
from book_club.util.DatasetLoad import *
from surprise.model_selection import train_test_split
import random

def getAntiTestSetForClub(clubId, trainSet):
    """ Return the anti-test set for this club """
    trainset = trainSet
    fill = trainset.global_mean
    anti_testset = []
    c = trainset.to_inner_uid(int(clubId))
    club_items = set([j for (j, _) in trainset.ur[c]])
    anti_testset += [(trainset.to_raw_uid(c), trainset.to_raw_iid(i), fill) for
                             i in trainset.all_items() if
                             i not in club_items]
    return anti_testset


def getMatch(rating):
    """ Return a % match for a rating """
    if int(rating) == 10:
        return 100
    x = 80
    for i in range(1,int(rating)+1):
        x += 2
    return random.randint(x,x+1)


def getTopNRecs(clubId):
    """ Return the top-N recommendation for club_id """

    reader = Reader(rating_scale=(1, 10))
    df = get_clubs_ratings_df()

    class MyDataset(dataset.DatasetAutoFolds):
        def __init__(self, df, reader):
            self.raw_ratings = [(uid, iid, r, None) for (uid, iid, r) in
                    zip(df['userid'], df['isbn'], df['bookrating'])]
            self.reader = reader

    data = MyDataset(df, reader)

    trainSet, testSet = train_test_split(data, test_size=.20, random_state=1)
    antiTestSet = getAntiTestSetForClub(clubId, trainSet)

    model = SVD(random_state=10)
    model.fit(trainSet)
    predictions = model.test(antiTestSet)

    books = models.Book.objects.all()
    recommendations = []
    current_club = models.Club.objects.get(id=clubId)
    list = models.ClubReadingList.objects.filter(club=current_club)
    book_list = []
    for b in list:
        book_list.append(b.book)
    current_book = models.CurrentlyReading.get_currently_reading(current_club)

    for clubId, bookId, actualRating, estimatedRating, _ in predictions:
        strBookId = str(bookId)
        try:
            book = books.get(ISBN=strBookId)
            if (book not in book_list) or (book is not current_book) :
                recommendations.append((book, estimatedRating))
                recommendations.sort(key=lambda x: x[1], reverse=True)
        except ObjectDoesNotExist:
            pass

    if len(recommendations) < 10:
        return getTopPopularBooks()
    else:
        rec = []
        for b, e in recommendations[:10]:
            match = getMatch(e)
            rec.append((b,match))
            rec.sort(key=lambda x: x[1], reverse=True)
        return rec
