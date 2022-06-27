import json


class CourseEncoder(json.JSONEncoder):

    def default(self, o):
        return o.__dict__
