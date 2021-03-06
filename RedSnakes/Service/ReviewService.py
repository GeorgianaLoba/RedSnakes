import json

from ConferenceManager import serializers
from ConferenceManager.models import Abstract, Bid, ConferenceAuthor, ConferenceAuthorSession, \
    ConferenceSession, Review
from RedSnakes.Service.MainService import MainService


class ReviewService(MainService):
    def __init__(self):
        super().__init__()

    def add(self, review):
        review = json.loads(review)
        serializer = serializers.ReviewSerializer(data=review)
        if not serializer.is_valid():
            raise ValueError('Invalid JSON!', serializer.errors)
        new_review = serializer.create(serializer.validated_data)
        Review.save(new_review)

    def update(self, entity):
        pass

    def getAll(self):
        reviews = Review.objects.all().order_by('paperId')
        reviews_json = serializers.FullReviewSerializer(reviews, many=True)
        return reviews_json

    def get_by_id(self, review_id: int):
        # FIXME Possibly unused?
        review = Review.objects.get(pk=review_id)
        review_json = serializers.ReviewSerializer(review)
        return review_json

    def delete(self, entity):
        pass

    def add_bid(self, bid):
        bid = json.loads(bid)
        serializer = serializers.BidSerializer(data=bid, many=True)
        if not serializer.is_valid():
            raise ValueError('Invalid JSON!', serializer.errors)
        new_bids = serializer.create(serializer.validated_data)
        for bid in new_bids:
            # If the bid for the same paper and PCmember already exists, update it
            # Otherwise, add a new Bid
            try:
                bid_in_db = Bid.objects.get(abstractId=bid.abstractId, pcId=bid.pcId)
            except Exception:
                bid_in_db = False
            if bid_in_db is not False:
                bid_in_db.status = bid.status
                bid_in_db.save()
            else:
                Bid.save(bid)

    def add_section(self, section, papers):
        serializer_section = serializers.ConferenceSessionSerializer(data=section)
        serializer_papers = serializers.PaperSerializer(data=papers, many=True)
        if not serializer_section.is_valid() or not serializer_papers.is_valid():
            raise ValueError('Invalid JSON!')
        new_section = serializer_section.create(serializer_section.validated_data)
        ConferenceSession.save(new_section)

        papers_list = []
        for paper in serializer_papers.validated_data:
            papers_list.append(serializer_papers.create(paper))

        authors_list = []
        for paper in papers_list:
            abstract = Abstract.objects.get(pk=paper.paperId)
            author = ConferenceAuthor.objects.get(pk=abstract.authorId)
            authors_list.append(author)

        for author in authors_list:
            conf_auth_session = ConferenceAuthorSession()
            conf_auth_session.conferenceAuthorId = author.pk
            conf_auth_session.conferenceSessionId = new_section.pk
            ConferenceAuthorSession.save(conf_auth_session)
