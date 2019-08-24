from elasticsearch import Elasticsearch
from people_counter.simple_classes import DbType


class DbConnector:
    def __init__(self, db_type: DbType,
                 host,
                 port,
                 business_id="cafe124",
                 shop_id="sottocorno17",
                 db_name="people-counter"):
        self.db_type = db_type
        if db_type == DbType.ELASTIC:
            self.mappings = {
                "mappings": {
                    "properties": {
                        "shop_id": {"type": "keyword"},
                        "business_id": {"type": "keyword"},
                        "customer": {"type": "keyword"},
                        "camera": {"type": "keyword"},
                        "previous_visit": {"type": "integer"},
                        "visit_date": {
                            "type": "date",
                            "format": "strict_date_optional_time||epoch_millis"
                        }
                    }
                }
            }
            self.db = Elasticsearch([{'host': host, 'port': port}])

        self.business_id = business_id
        self.shop_id = shop_id
        self.db_name = db_name

    def create_db(self):
        if self.db_type == DbType.ELASTIC:
            self.db.indices.delete(index=self.db_name)
            self.db.indices.create(index=self.db_name, body=self.mappings)

    def from_logfile(self, filename: str,
                     from_date: int=0,
                     to_date: int=9999999999999):
        """
        Load data in the logfile into the db
        :param filename:
        :param from_date: load only data happening after
        :return:
        """
        if self.db_type == DbType.ELASTIC:
            faces = {}
            faces_es = []

            with open(filename) as f:
                for line in f.readlines():
                    line = line.split(",")
                    if from_date < int(line[0]) < to_date:
                        if faces.get(int(line[1])) is not None:
                            previous_visit = (faces.get(int(line[1]))[-1]["visit_date"] - int(line[0])) / 86400000
                            faces[int(line[1])].append({"business_id": self.business_id, "shop_id": self.shop_id,
                                                        "customer": int(line[1]), "visit_date": int(line[0]),
                                                        "camera": line[6].strip(), "previous_visit": previous_visit})
                        else:
                            faces[int(line[1])] = [{"business_id": self.business_id, "shop_id": self.shop_id,
                                                    "customer": int(line[1]), "visit_date": int(line[0]),
                                                    "camera": line[6].strip(), "previous_visit": 0}]

                        faces_es.append(faces[int(line[1])][-1])
            for e in faces_es:
                self.db.index(index=self.db_name, body=e)
