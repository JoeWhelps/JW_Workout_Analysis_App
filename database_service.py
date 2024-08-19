# 
import pandas as pd
import harperdb

url = "https://cloud1-joewhelpley.harperdbcloud.com"
user = "guest"
password = "Guest24!!"

db = harperdb.HarperDB(
    url=url,
    username=user,
    password=password
)

SCHEMA = "workout_repo"
TABLE = "workouts"
TABLE_TODAY = "workout_today"
WORK = "workout_table"

def insert_workout(workout_data):
    return db.insert(SCHEMA, TABLE, [workout_data])

def delete_workout(workout_id):
    return db.delete(SCHEMA, TABLE, [workout_id])

def get_all_workouts():
    try:
        return db.sql(f"select video_id,channel,title,duration from {SCHEMA}.{TABLE}")
    except harperdb.exceptions.HarperDBError:
        return []

def get_workout_today():
    return db.sql(f"select * from {SCHEMA}.{TABLE_TODAY} where id = 0")

def update_workout_today(workout_data, insert=False):
    workout_data['id'] = 0
    if insert:
        return db.insert(SCHEMA, TABLE_TODAY, [workout_data])
    return db.update(SCHEMA, TABLE_TODAY, [workout_data])

# workout track functions
def fetch_workout_data():
    try:
        # Fetch data from HarperDB
        response = db.sql(f"SELECT * FROM {SCHEMA}.{WORK}")
        
        # Ensure response is a list of dictionaries
        if isinstance(response, list) and all(isinstance(record, dict) for record in response):
            # Normalize JSON data into a DataFrame
            df = pd.json_normalize(response)
            
            # Convert JSON strings to dictionaries if needed
            df['workouts'] = df['workouts'].apply(lambda x: eval(x) if isinstance(x, str) else x)
            
            return df
        else:
            raise ValueError("Unexpected response format")
    
    except Exception as e:
        print("Error fetching data:", e)
        raise

def delete_workout_entry(workout_id):
    return db.delete(SCHEMA, WORK, [workout_id])

def update_work(workout_ds):
    return db.update(SCHEMA, WORK, [workout_ds])

def get_all_info():
    try:
        return db.sql(f"select workouts from {SCHEMA}.{WORK}")
    except harperdb.exceptions.HarperDBError:
        return []
    


'''
data = {
    "video_id": "12345",
    "title":"Test 1",
    "channel":"Test channel"
}

res = db.insert(SCHEMA,TABLE, [data])
print(res)
'''