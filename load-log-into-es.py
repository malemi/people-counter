from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

faces = {}
faces_es = []

business_id = "cafe124"
shop_id = "sottocorno17"

with open("face_detected.log") as f:
    for line in f.readlines():
        line = line.split(",")
        if faces.get(line[1]) is not None:
            previous_visit = (faces.get(line[1])[-1]["visit_date"] - int(line[0])) / 86400000
            faces[line[1]].append({"business_id": business_id, "shop_id": shop_id,
                                   "customer": line[1], "visit_date": int(line[0]),
                                   "camera": line[6].strip(), "previous_visit": previous_visit})
        else:
            faces[line[1]] = [{"business_id": business_id, "shop_id": shop_id,
                               "customer": line[1], "visit_date": int(line[0]),
                               "camera": line[6].strip(), "previous_visit": 0}]

        faces_es.append(faces[line[1]][-1])
            
mappings = {
  "mappings": {
    "properties": {
        "shop_id":  {"type": "keyword"},
        "business_id":  {"type": "keyword"},
        "customer": {"type": "keyword"},
        "camera": {"type": "keyword"},
        "previous_visit":      {"type": "integer"},
        "visit_date":  {
            "type":   "date",
            "format": "strict_date_optional_time||epoch_millis"
      }
    }
  }
}

index_name = "people-counter"

es.indices.delete(index=index_name)
es.indices.create(index=index_name, body=mappings)

for e in faces_es:
    es.index(index=index_name, body=e)

# es.get(index=index_name, body={'query':{}})
