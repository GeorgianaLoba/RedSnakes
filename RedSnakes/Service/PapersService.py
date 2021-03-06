import json

from ConferenceManager import serializers
from ConferenceManager.models import Abstract , Bid , ConferenceAuthorSession , Paper , ConferenceAuthor , Participant
from RedSnakes.Service.MainService import MainService


class PapersService(MainService):
    def __init__(self):
        super().__init__()

    def add(self, entity):
        paper = json.loads(entity)
        serializer = serializers.PaperSerializer(data=paper)
        if not serializer.is_valid():
            raise ValueError('Invalid JSON!', serializer.errors)
        new_paper = serializer.create(serializer.validated_data)
        Paper.save(new_paper)

    def update(self, entity):
        pass

    def delete(self, entity):
        pass

    def getAll(self):
        papers = Paper.objects.all().order_by('paperId')
        papers_json = serializers.PaperSerializer(papers, many=True)
        return papers_json

    def getAllNotInSections(self):
        papers = Paper.objects.all().order_by('paperId')
        filtered_papers = []
        for paper in papers:
            if ConferenceAuthorSession.objects.filter(
                    conferenceAuthorId=paper.paperId.authorId).count() == 0:
                filtered_papers.append(paper)
        papers_json = serializers.PaperSerializer(filtered_papers, many=True)
        return papers_json

    def getById(self, paper_id: int):
        paper = Paper.objects.get(pk=paper_id)
        paper_json = serializers.PaperSerializer(paper)
        return paper_json

    def assign_title(self, content_json):
        print("assign_title --- entered")
        print(content_json)
        content_json = json.loads(content_json)
        abstract = Abstract.objects.get(title=content_json['title'])
        Abstract.objects.filter(title=content_json['title']).update(text=content_json['content'])
        print(abstract)

    def sendAbstract(self, abstract_json):
        print("sendAbstract --- entered")
        print(abstract_json)
        abstract_json = json.loads(abstract_json)
        #serializer = serializers.AbstractSerializer(data=abstract_json)
        participant = Participant.objects.get(name=abstract_json['authorId'])
        authorId = ConferenceAuthor.objects.get(pEmail=participant)
        print(authorId)
        a = Abstract(authorId=authorId, text = "empty", title=abstract_json['title'])
        a.save()
        p=Paper(paperId=a, path="snails.pdf", accepted=False)
        p.save()
        #FIXME maybe

        # paperId = models.OneToOneField(Abstract, on_delete=models.CASCADE)
        # path = models.CharField(max_length=255, null=False)
        # accepted = models.BooleanField(null=True)

        '''if not serializer.is_valid():
            print("Serializer --- entered")
            print(serializer.errors)
            raise ValueError('Invalid JSON!', serializer.errors)
        abstract = serializer.create(serializer.validated_data)
        print("HERE2")
        Abstract.save()
        return abstract'''


    def assignReviewer(self, bid):
        bid = json.loads(bid)
        serializer = serializers.BidSerializer(data=bid, many=True)
        if not serializer.is_valid():
            raise ValueError('Invalid JSON!', serializer.errors)
        print(serializer.validated_data)
        new_bids = serializer.create(serializer.validated_data)
        for bid in new_bids:
            bid_in_db = Bid.objects.get(abstractId=bid.abstractId, pcId=bid.pcId)
            bid_in_db.chosenToReview = True
            bid_in_db.save()

    def getBidsForOnePaper(self, abstract_id):
        bids = Bid.objects.all().order_by('abstractId')
        abstract = Abstract.objects.get(pk=abstract_id)
        paperBids = []
        for bid in bids:
            if bid.abstractId == abstract and bid.status is True and not bid.chosenToReview:
                paperBids.append(bid)
        bids_json = serializers.FullBidSerializer(paperBids, many=True)
        return bids_json
