import psycopg2
import queries
import time

# Configuration

db_host = "localhost"
database = "pplcounter"
db_user = "mal"
table_name = "visits"

session = queries.Session('postgresql://' + db_user + '@' + db_host + '/' + database)

set_timezone = "SET timezone = 'Europe/Rome';"

drop_table = "drop table {};".format(table_name)

create_table = """create table {}(
uuid UUID,
visit_ts TIMESTAMPTZ,
days_previous_visit int,
business_id text,
shop_id text,
camera_location text,
primary key (visit_ts, uuid));""".format(table_name)

session.query(set_timezone)
try:
    session.query(drop_table)
    print("Drop table {}".format(table_name))
except psycopg2.errors.UndefinedTable:
    print("Table {} does not exist".format(table_name))

session.query(create_table)

business_id = "cafe124"
shop_id = "sottocorno17"

faces_dict = {}
faces_rows = []

with open("face_detected.log") as f:
    for line in f.readlines():
        line = line.split(",")
        visit_ts = time.strftime('%Y-%m-%d %H:%M:%S-00', time.localtime(int(line[0]) / 1000))
        # Compute hours since last visit (if any)
        # TODO must be done retrieving data from DB
        if faces_dict.get(line[1]) is not None:

            days_previous_visit = abs(round((faces_dict.get(line[1])[-1]["visit_epoch_ms"] - int(line[0])) / 86400000))
            faces_dict[line[1]].append({"business_id": business_id, "shop_id": shop_id,
                                        "uuid": line[1], "visit_ts": visit_ts,
                                        "visit_epoch_ms": int(line[0]),
                                        "camera_location": line[6].strip(), "days_previous_visit": days_previous_visit})
        else:
            faces_dict[line[1]] = [{"business_id": business_id, "shop_id": shop_id,
                                    "uuid": line[1], "visit_ts": visit_ts,
                                    "visit_epoch_ms": int(line[0]),
                                    "camera_location": line[6].strip(), "days_previous_visit": 0}]

        faces_rows.append(faces_dict[line[1]][-1])

for row in faces_rows:
    session.query("insert into {0}(uuid, visit_ts, days_previous_visit, business_id, shop_id, camera_location) ".format(table_name) +
                  "values('{0}', '{1}', {2}, '{3}', '{4}', '{5}')".format(row["uuid"], row["visit_ts"],
                                                                          row["days_previous_visit"], row["business_id"],
                                                                          row["shop_id"], row["camera_location"],
                                                                          table_name))

