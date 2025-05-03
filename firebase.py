import datetime
import uuid

import firebase_admin
from firebase_admin import auth, credentials, firestore

cred = credentials.Certificate(
    "diabeticvirtualassistant-firebase-adminsdk-fbsvc-523bab06ab.json"
)
firebase_admin.initialize_app(cred)

db = firestore.client()


############################User#######################
def login_user(email):
    user = None
    try:
        user = auth.get_user_by_email(email)
        return user
    except Exception as e:
        print("Cannot log this user in")
    finally:
        return user


def get_users():
    docs = db.collection("users").stream()
    thisUser = {}
    fb_users = []
    for doc in docs:
        thisUser = doc.to_dict()
        thisUser["userid"] = doc.id
        fb_users.append(thisUser)
    return fb_users


###############################FOOD############################3
def get_food():
    docs = db.collection("foods").stream()
    fb_foods = []
    thisFood = {}
    for doc in docs:
        thisFood = doc.to_dict()
        thisFood["foodid"] = doc.id
        fb_foods.append(thisFood)
    return fb_foods


def delete_food(id):
    db.collection("foods").document(id).delete()
    return id


def add_food(data, user, type, dtime, random_uuid):
    data["type"] = type
    data["userid"] = user["userid"]
    data["datetime"] = datetime.datetime.strptime(dtime, "%Y-%m-%d %H:%M:%S")
    batch = db.batch()
    food_ref = db.collection("foods").document(f"{random_uuid}")
    batch.set(food_ref, data)
    batch.commit()


def get_food_by_person(id):
    food_by_person = []
    fb_foods = get_food()
    if len(fb_foods) != 0:
        food_by_person = [food for food in fb_foods if food["userid"] == id]
    return food_by_person


####Weights########################
def add_weight(data, user, date, random_uuid):
    data["userid"] = user["userid"]
    data["Date"] = date
    batch = db.batch()
    weight_ref = db.collection("weights").document(f"{random_uuid}")
    batch.set(weight_ref, data)
    batch.commit()


def get_weights():
    docs = db.collection("weights").stream()
    fb_weights = []
    for doc in docs:
        fb_weights.append({**{"weightid": doc.id}, **doc.to_dict()})
    return fb_weights


def get_weights_by_person(id):
    weight_by_person = []
    fb_weights = get_weights()
    if (fb_weights) != 0:
        weight_by_person = [weight for weight in fb_weights if weight["userid"] == id]
    return weight_by_person


def delete_weight(id):
    db.collection("weights").document(id).delete()
    return id


##################Water ##############################
def add_water(data, user, date, random_uuid):
    data["userid"] = user["userid"]
    data["Date"] = date
    batch = db.batch()
    water_ref = db.collection("water").document(f"{random_uuid}")
    batch.set(water_ref, data)
    batch.commit()


##################BloodSugars#########################
def get_bloodsugars():
    docs = db.collection("bloodsugars").stream()
    fb_bloodsugars = []
    for doc in docs:
        fb_bloodsugars.append({**{"bloodsugarid": doc.id}, **doc.to_dict()})
    return fb_bloodsugars


def get_bloodsugars_by_person(id):
    bloodsugar_by_person = []
    fb_bloodsugars = get_bloodsugars()
    if (fb_bloodsugars) != 0:
        bloodsugar_by_person = [
            bloodsugar for bloodsugar in fb_bloodsugars if bloodsugar["userid"] == id
        ]
    return bloodsugar_by_person


######################Exercise#########################
def add_exercise(data, user, date, random_uuid):
    data["userid"] = user["userid"]
    data["Date"] = date
    batch = db.batch()
    exercise_ref = db.collection("exercises").document(f"{random_uuid}")
    batch.set(exercise_ref, data)
    batch.commit()


def get_exercise():
    docs = db.collection("exercises").stream()
    fb_exercises = []
    for doc in docs:
        fb_exercises.append({**{"exerciseid": doc.id}, **doc.to_dict()})
    return fb_exercises


def get_exercise_by_person(id):
    exercise_by_person = []
    fb_exercises = get_exercise()
    if (fb_exercises) != 0:
        exercise_by_person = [
            exercise for exercise in fb_exercises if exercise["userid"] == id
        ]
    return exercise_by_person


#################### Sleep ###########################################


def add_sleep(data, user, date, random_uuid):
    data["userid"] = user["userid"]
    data["Date"] = date
    batch = db.batch()
    water_ref = db.collection("sleep").document(f"{random_uuid}")
    batch.set(water_ref, data)
    batch.commit()


def get_sleep():
    docs = db.collection("sleep").stream()
    fb_sleep = []
    for doc in docs:
        fb_sleep.append({**{"sleepid": doc.id}, **doc.to_dict()})
    return fb_sleep


def get_sleep_by_person(id):
    sleep_by_person = []
    fb_sleep = get_exercise()
    if (fb_sleep) != 0:
        sleep_by_person = [sleep for sleep in fb_sleep if sleep["userid"] == id]
    return sleep_by_person


########################### Food Understanding ##########################


def add_food_understanding(data, user, date, random_uuid):
    data["userid"] = user["userid"]
    data["Date"] = date
    batch = db.batch()
    food_understanding_ref = db.collection("foodunderstanding").document(
        f"{random_uuid}"
    )
    batch.set(food_understanding_ref, data)
    batch.commit()
