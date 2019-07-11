from elasticsearch import Elasticsearch

es = Elasticsearch([{'host':'localhost','port':9200}])

faces = {}
faces_es = []

with open("face_detected.log") as f:
    for l in f.readlines():
        l = l.split(",")
        if faces.get(int(l[1])) is not None:
            previous_visit = (faces.get(int(l[1]))[-1]["visit_date"] - l[0]) / 86400000
            faces[int(l[1])].append({"customer": int(l[1]), "visit_date": int(l[0]),
                                     "camera": l[6].strip(), "previous_visit": previous_visit})
        else:
            faces[int(l[1])] = [{"customer": int(l[1]), "visit_date": int(l[0]),
                                 "camera": l[6].strip(), "previous_visit": 0}]

        faces_es.append(faces[int(l[1])][-1])
            
mappings = {
  "mappings": {
    "properties": { 
      "customer":    { "type": "text"}, 
      "camera":     { "type": "text"  }, 
      "previous_visit":      { "type": "integer" },  
      "visit_date":  {
        "type":   "date", 
        "format": "strict_date_optional_time||epoch_millis"
      }
    }
  }
}

index_name = "cafe124"

es.indices.delete(index=index_name)
es.indices.create(index=index_name, body=mappings)

for e in faces_es:
    es.index(index=index_name, body=e)

# es.get(index=index_name, body={'query':{}})
