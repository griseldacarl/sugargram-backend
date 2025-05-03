import json
import os
import uuid
from datetime import date, datetime, timedelta, timezone
from operator import itemgetter

import pandas as pd
from firebase import (
    add_exercise,
    add_food,
    add_food_understanding,
    add_sleep,
    add_water,
    add_weight,
    delete_food,
    get_bloodsugars,
    get_bloodsugars_by_person,
    get_exercise_by_person,
    get_food_by_person,
    get_users,
    get_weights_by_person,
    login_user,
)
from flask import Flask, jsonify, redirect, render_template, request, session
from flask_session import Session
from prediction import get_prediction

df = pd.read_csv("static/food101_nutrition.csv")
df["name"] = df["label"]
df = df.set_index("label")

thisdir = os.getcwd()
imagedir = os.path.join(thisdir, "static/images")
food_images = []
food_names = []
foods = []
for r, d, f in os.walk(imagedir):
    for file in f:
        if file.endswith(".jpg"):
            food_images.append(os.path.join("static/images/", file))
            food_names.append("" + file[:-4] + "")

for i in range(len(food_names)):
    foods.append(
        {
            "name": df.loc[food_names[i]].name,
            "weight": df.loc[food_names[i]].weight,
            "calories": df.loc[food_names[i]].calories,
            "protein": df.loc[food_names[i]].protein,
            "carbohydrates": df.loc[food_names[i]].carbohydrates,
            "fats": df.loc[food_names[i]].fats,
            "fiber": df.loc[food_names[i]].fiber,
            "sugars": df.loc[food_names[i]].sugars,
            "sodium": df.loc[food_names[i]].sodium,
            "image": food_images[i],
        }
    )


workouts = [
    {"Body Part": "Chest", "Workout": "Incline dumbbell press"},
    {"Body Part": "Chest", "Workout": "Incline cable crossovers"},
    {"Body Part": "Chest", "Workout": "Incline dumbbell flyes"},
    {"Body Part": "Chest", "Workout": "Decline dumbbell press"},
    {"Body Part": "Chest", "Workout": "Decline cable crossovers"},
    {"Body Part": "Chest", "Workout": "Decline dumbbell flyes"},
    {"Body Part": "Chest", "Workout": "Chest flyes"},
    {"Body Part": "Chest", "Workout": "Cable crossovers"},
    {"Body Part": "Chest", "Workout": "Dumbbell flyes"},
    {"Body Part": "Back", "Workout": "Pull-ups"},
    {"Body Part": "Back", "Workout": "Barbell rows"},
    {"Body Part": "Back", "Workout": "Dumbbell rows"},
    {"Body Part": "Back", "Workout": "Seated cable rows"},
    {"Body Part": "Back", "Workout": "Bent-over rows"},
    {"Body Part": "Back", "Workout": "Hyperextensions"},
    {"Body Part": "Back", "Workout": "Bird dog"},
    {"Body Part": "Arms", "Workout": "Barbell curls"},
    {"Body Part": "Arms", "Workout": "Dumbbell curls"},
    {"Body Part": "Arms", "Workout": "Preacher curls"},
    {"Body Part": "Arms", "Workout": "Hammer curls"},
    {"Body Part": "Arms", "Workout": "Concentration curls"},
    {"Body Part": "Arms", "Workout": "Close-grip bench press"},
    {"Body Part": "Arms", "Workout": "Overhead triceps extensions"},
    {"Body Part": "Arms", "Workout": "Triceps pushdowns"},
    {"Body Part": "Arms", "Workout": "Skull crushers"},
    {"Body Part": "Arms", "Workout": "Triceps dips"},
    {"Body Part": "Legs", "Workout": "Barbell squats"},
    {"Body Part": "Legs", "Workout": "Leg press"},
    {"Body Part": "Legs", "Workout": "Leg extensions"},
    {"Body Part": "Legs", "Workout": "Romanian deadlifts"},
    {"Body Part": "Legs", "Workout": "Leg curls"},
    {"Body Part": "Legs", "Workout": "Barbell hip thrusts"},
    {"Body Part": "Legs", "Workout": "Donkey kicks"},
    {"Body Part": "Legs", "Workout": "Standing calf raises"},
    {"Body Part": "Legs", "Workout": "Seated calf raises"},
    {"Body Part": "Shoulders", "Workout": "Dumbbell front raises"},
    {"Body Part": "Shoulders", "Workout": "Military press"},
    {"Body Part": "Shoulders", "Workout": "Lateral raises"},
    {"Body Part": "Shoulders", "Workout": "Bent-over lateral raises"},
    {"Body Part": "Shoulders", "Workout": "Face pulls"},
    {"Body Part": "Abs", "Workout": "Crunches"},
    {"Body Part": "Abs", "Workout": "Leg raises"},
    {"Body Part": "Abs", "Workout": "Bicycle crunches"},
    {"Body Part": "Abs", "Workout": "Russian twists"},
    {"Body Part": "Abs", "Workout": "Hanging leg raises"},
    {"Body Part": "Abs", "Workout": "Plank"},
    {"Body Part": "Forearms", "Workout": "Wrist curl"},
    {"Body Part": "Forearms", "Workout": "Wrist extension"},
    {"Body Part": "Forearms", "Workout": "Plate pinch"},
    {"Body Part": "Forearms", "Workout": "Towel pull-up"},
    {"Body Part": "Forearms", "Workout": "Fat grip dumbbell curl"},
    {"Body Part": "Forearms", "Workout": "Hammer curl"},
]

app = Flask(__name__)
SESSION_TYPE = "filesystem"
app.config.from_object(__name__)
Session(app)


# define function for convert yyyy-mm-dd to dd-mm-yyyy
def format_datetime(value, format="%Y-%m-%d %H:%M:%S"):
    if value is None:
        return ""
    return value.strftime(format)


# configured Jinja2 environment with user defined
app.jinja_env.filters["date_format"] = format_datetime


############################### GAME######################


@app.route("/add-food-understanding-data", methods=["POST"])
def add_food_understanding_data():
    food_understanding = request.json
    data = {"status": "success"}
    random_uuid = uuid.uuid4()
    today_date = datetime.now()
    add_food_understanding(
        food_understanding,
        session["current_user"],
        today_date.strftime("%Y-%m-%d"),
        random_uuid,
    )
    return jsonify(data)


###############################MAIN ROUTES###################3
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    email = request.form.get("useremail")
    auth_user = login_user(email)
    current_user = None
    if auth_user is not None:
        db_users = get_users()
        current_user = [user for user in db_users if auth_user.email == user["email"]]
        session["current_user"] = current_user[0]
        return render_template("dialog.html", email=email, user=current_user[0])
    return "<h1>Login Failed</h1>"


@app.route("/SignIn")
def signin():
    session["current_user"] = None
    return render_template("login.html")


@app.route("/DiaBuddy")
def game():
    curr_user = session["current_user"]
    if curr_user == None:
        return redirect("/SignIn")
    else:
        return render_template("game.html", foods=foods, user=session["current_user"])


############################################DIALOG############################################


@app.route("/add-food-form")
def add_food_form():
    return render_template("add_food_form.html", foods=foods)


@app.route("/add-food-prediction-form")
def add_food_prediction_form():
    return render_template("add_food_prediction_form.html", foods=foods)


@app.route("/predict-add-food", methods=["POST"])
def add_food_prediction():
    imagefile = request.files["imagefile"]
    image_path = "./static/tmp/" + imagefile.filename
    imagefile.save(image_path)
    result = get_prediction(imagefile)
    food = [food for food in foods if food.get("name") == result["result"]]
    return render_template("accept_or_rejected_prediction.html", food=food[0])


@app.route("/add-food-prediction-comfirmed", methods=["GET"])
def add_predicted_food_today():
    food = {
        "name": request.args.get("name"),
        "weight": request.args.get("weight"),
        "calories": request.args.get("calories"),
        "protein": request.args.get("protein"),
        "carbohydrates": request.args.get("carbohydrates"),
        "fats": request.args.get("fats"),
        "fiber": request.args.get("fiber"),
        "sugars": request.args.get("sugars"),
        "sodium": request.args.get("sodium"),
    }
    foodtype = request.args.get("foodtype")
    random_uuid = uuid.uuid4()
    today_date = datetime.now()
    add_food(
        food,
        session["current_user"],
        foodtype,
        today_date.strftime("%Y-%m-%d %H:%M:%S"),
        random_uuid,
    )
    print(foodtype)
    return redirect("/add-food-prediction-form")


@app.route("/food-list-diaglog/add", methods=["POST"])
def add_food_to_database():
    data = request.form.get("foodselection")
    foodtype = request.form.get("foodtype")
    food = json.loads(data)
    random_uuid = uuid.uuid4()
    today_date = datetime.now()
    add_food(
        food,
        session["current_user"],
        foodtype,
        today_date.strftime("%Y-%m-%d %H:%M:%S"),
        random_uuid,
    )
    return redirect("/add-food-form")


#################################################Profile#########################################
@app.route("/profile")
def profile():
    loginstatus = "logout"
    current_user = None
    if "current_user" in session:
        loginstatus = "login"
        current_user = session["current_user"]
    else:
        loginstatus = "logout"
        current_user = None

    return render_template(
        "profile.html", loginstatus=loginstatus, current_user=current_user
    )


@app.route("/total-weight-lost-profile")
def total_weight_lost_profile():
    return render_template("total_weight_lost_profile.html")


@app.route("/total-weight-lost-data")
def get_total_weight_lost():
    current_user = session.get("current_user", "No current user is set")
    weights_data = get_weights_by_person(current_user.get("userid"))
    sorted_weights_data = sorted(weights_data, key=itemgetter("Date"))
    labels = [sorted_weights_data[0].get("Date"), sorted_weights_data[-1].get("Date")]
    values = [
        sorted_weights_data[0].get("Weight(pounds)"),
        sorted_weights_data[-1].get("Weight(pounds)"),
    ]
    data = {"labels": labels, "values": values}
    return jsonify(data)


#########################################DASHBOARD###################################
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/calories-summary-dashboard")
def calories_summary_dashboard():
    return render_template("calories_summary_today_dashboard.html")


@app.route("/calories-eaten-summary-for-current-date-data")
def get_calories_eaten_summary_for_current_date_data():
    # Sample data (replace with your data processing logic)
    current_user = session.get("current_user", "No current user is set")
    food_by_person = get_food_by_person(current_user.get("userid"))
    today_date = date.today()
    labels = ["Breakfast", "Lunch", "Dinner", "Snack"]
    breakfast = [
        float(food.get("calories"))
        for food in food_by_person
        if food.get("datetime").date() == today_date and food.get("type") == "breakfast"
    ]
    dinner = [
        float(food.get("calories"))
        for food in food_by_person
        if food.get("datetime").date() == today_date and food.get("type") == "dinner"
    ]
    lunch = [
        float(food.get("calories"))
        for food in food_by_person
        if food.get("datetime").date() == today_date and food.get("type") == "lunch"
    ]
    snack = [
        float(food.get("calories"))
        for food in food_by_person
        if food.get("datetime").date() == today_date and food.get("type") == "snack"
    ]
    calories = [
        sum(breakfast),
        sum(lunch),
        sum(dinner),
        sum(snack),
    ]
    data = {"labels": labels, "values": calories}
    return jsonify(data)


@app.route("/weight-summary-dashboard")
def weight_summary_dashboard():
    return render_template("weight_summary_dashboard.html")


@app.route("/weight-summary-data")
def get_weight_summary_data():
    # Sample data (replace with your data processing logic)
    current_user = session.get("current_user", "No current user is set")
    weights_data = get_weights_by_person(current_user.get("userid"))
    sorted_weights_data = sorted(weights_data, key=itemgetter("Date"))
    last_four_weights_data = sorted_weights_data[-4:]
    labels = [weight.get("Date") for weight in last_four_weights_data]
    values = [weight.get("Weight(pounds)") for weight in last_four_weights_data]
    data = {"labels": labels, "values": values}
    return jsonify(data)


#############################################################


@app.route("/logbook")
def logbook():
    return render_template("logbook.html")


################################################STATISTICS#############################
@app.route("/statistics")
def statistics():
    return render_template("statistics.html")


@app.route("/totat-bloodsugar-data")
def get_total_bloodsugar_data():
    current_user = session.get("current_user", "No current user is set")
    bloodsugars_data = get_bloodsugars_by_person(current_user.get("userid"))
    sorted_bloodsugars_data = sorted(bloodsugars_data, key=itemgetter("DateTime"))
    most_recent_bloodsugar_data = sorted_bloodsugars_data[-10:]
    labels = [bloodsugar.get("DateTime") for bloodsugar in most_recent_bloodsugar_data]
    values = [
        bloodsugar.get("BloodSugarLevel(mg/dl)")
        for bloodsugar in most_recent_bloodsugar_data
    ]
    data = {"labels": labels, "values": values}
    return jsonify(data)


@app.route("/total-bloodsugar-statistics")
def show_bloodsugar_statistics():
    return render_template("show_bloodsugar_statistics.html")


@app.route("/total-weight-data")
def get_total_weight_data():
    current_user = session.get("current_user", "No current user is set")
    weights_data = get_weights_by_person(current_user.get("userid"))
    sorted_weights_data = sorted(weights_data, key=itemgetter("Date"))
    last_four_weights_data = sorted_weights_data[-10:]
    labels = [weight.get("Date") for weight in last_four_weights_data]
    values = [weight.get("Weight(pounds)") for weight in last_four_weights_data]
    data = {"labels": labels, "values": values}
    return jsonify(data)


@app.route("/total-weight-statistics")
def show_weight_statistics():
    return render_template("show_weight_statistics.html")


@app.route("/total-exercise-statistics")
def show_exercise_statistics():
    current_user = session.get("current_user", "No current user is set")
    exercise_data = get_exercise_by_person(current_user.get("userid"))
    sorted_exercises_data = sorted(exercise_data, key=itemgetter("Date"))
    most_recent_exercises_data = sorted_exercises_data[-10:]
    return render_template(
        "show_exercise_statistics.html", exercises=most_recent_exercises_data
    )


@app.route("/total-food-statistics")
def show_food_statistics():
    current_user = session.get("current_user", "No current user is set")
    food_by_person = get_food_by_person(current_user.get("userid"))
    sorted_food_data = sorted(food_by_person, key=itemgetter("datetime"))
    most_recent_food_data = sorted_food_data[-10:]
    return render_template("show_food_statistics.html", foods=most_recent_food_data)


#######################LOG BOOK################################
@app.route("/calories-remaining-logbook")
def calories_remaining_logbook():
    current_user = session.get("current_user", "No current user is set")
    food_by_person = get_food_by_person(current_user.get("userid"))
    session["food_by_selected_person"] = food_by_person
    today_date = date.today()
    formatted_date = today_date.strftime("%Y-%m-%d")
    calories = [
        float(food.get("calories"))
        for food in food_by_person
        if food.get("datetime").date() == today_date
    ]
    total_calories = sum(calories)
    yesterday = today_date - timedelta(days=1)
    tomorrow = today_date + timedelta(days=1)
    session["selected_date"] = today_date
    return render_template(
        "calories_remaining_logbook.html",
        calories=total_calories,
        date=formatted_date,
        yesterday=yesterday.strftime("%Y-%m-%d"),
        tomorrow=tomorrow.strftime("%Y-%m-%d"),
    )


@app.route("/calories-remaining-logbook/<string:currentdate>")
def calories_remaining_logbook_by_date(currentdate):
    current_user = session.get("current_user", "No current user is set")
    food_by_person = get_food_by_person(current_user.get("userid"))
    cdate = datetime.strptime(currentdate, "%Y-%m-%d").date()
    session["food_by_selected_person"] = food_by_person
    calories = [
        food.get("calories")
        for food in food_by_person
        if food.get("datetime").date() == cdate
    ]
    total_calories = sum(calories)
    yesterday = datetime.strptime(currentdate, "%Y-%m-%d") - timedelta(days=1)
    tomorrow = datetime.strptime(currentdate, "%Y-%m-%d") + timedelta(days=1)
    session["selected_date"] = cdate
    return render_template(
        "calories_remaining_logbook.html",
        calories=total_calories,
        date=currentdate,
        yesterday=yesterday.strftime("%Y-%m-%d"),
        tomorrow=tomorrow.strftime("%Y-%m-%d"),
    )


###################BREAKFAST#################################


@app.route("/breakfast-list-logbook")
def breakfast_list_logbook():
    food_by_person = session.get("food_by_selected_person")
    selected_date = session.get("selected_date")
    breakfast_for_date = [
        food
        for food in food_by_person
        if food.get("datetime").date() == selected_date
        and food.get("type").rfind("breakfast") != -1
    ]

    return render_template(
        "breakfast_list_logbook.html",
        date=selected_date,
        breakfastlist=breakfast_for_date,
    )


@app.route("/breakfast-list-logbook/add", methods=["POST"])
def do_add_breakfast_to_list_logbook():
    data = request.form.get("foodselection")
    food = json.loads(data)
    random_uuid = uuid.uuid4()
    today_date = datetime.now()
    add_food(
        food,
        session["current_user"],
        "breakfast",
        today_date.strftime("%Y-%m-%d %H:%M:%S"),
        random_uuid,
    )
    return f"""
             <li
    class="list-group-item d-flex justify-content-between align-items-center"
    key="{random_uuid}"
  >
    <div class="card" style="width: 18rem">
      <div class="card-header">{food.get('name')}</div>
      <div class="card-body">
        <ul class="list-group list-group-flush">
          <li class="list-group-item">
            Calories:&nbsp;<strong>{food.get('calories')}</strong>
          </li>
          <li class="list-group-item">
            Carbohydrates:&nbsp;<strong
              >{food.get('carbohydrates')}</strong
            >
          </li>
          <li class="list-group-item">
            Fats:&nbsp;<strong>{food.get('fats')}</strong>
          </li>
          <li class="list-group-item">
            Proteins:&nbsp;<strong>{food.get('protein')}</strong>
          </li>
        </ul>
      </div>
      <button
        hx-delete="/breakfast-list-logbook/delete/{random_uuid}"
        hx-target="closest li"
        type="button"
        class="btn btn-secondary"
      > Delete
      </button>
    </div>
  </li>
   <button
    hx-get="/breakfast-list-logbook/add-form"
    hx-target="this"
    hx-swap="outerHTML"
    type="button"
    class="btn btn-primary"
  >
    Add Breakfast
  </button>
 
           """


@app.route("/breakfast-list-logbook/delete/<string:foodid>", methods=["DELETE"])
def do_delete_breakfast_to_list_logbook(foodid):
    delete_food(foodid)
    return ""


@app.route("/breakfast-list-logbook/add-form")
def add_breakfast_to_list_logbook():
    return render_template("add_breakfast_food_form.html", foods=foods)


#####################################LUNCH#####################################
@app.route("/lunch-list-logbook")
def lunch_list_logbook():
    food_by_person = session.get("food_by_selected_person")
    selected_date = session.get("selected_date")
    lunch_for_date = [
        food
        for food in food_by_person
        if food.get("datetime").date() == selected_date
        and food.get("type").rfind("lunch") != -1
    ]

    return render_template(
        "lunch_list_logbook.html",
        date=selected_date,
        lunchlist=lunch_for_date,
    )


@app.route("/lunch-list-logbook/add-form")
def add_lunch_to_list_logbook():
    return render_template("add_lunch_food_form.html", foods=foods)


@app.route("/lunch-list-logbook/delete/<string:foodid>", methods=["DELETE"])
def do_delete_lunch_to_list_logbook(foodid):
    delete_food(foodid)
    return ""


@app.route("/lunch-list-logbook/add", methods=["POST"])
def do_add_lunch_to_list_logbook():
    data = request.form.get("lunchfoodselection")
    food = json.loads(data)
    random_uuid = uuid.uuid4()
    today_date = datetime.now()
    add_food(
        food,
        session["current_user"],
        "lunch",
        today_date.strftime("%Y-%m-%d %H:%M:%S"),
        random_uuid,
    )
    return f"""
             <li
    class="list-group-item d-flex justify-content-between align-items-center"
    key="{random_uuid}"
  >
    <div class="card" style="width: 18rem">
      <div class="card-header">{food.get('name')}</div>
      <div class="card-body">
        <ul class="list-group list-group-flush">
          <li class="list-group-item">
            Calories:&nbsp;<strong>{food.get('calories')}</strong>
          </li>
          <li class="list-group-item">
            Carbohydrates:&nbsp;<strong
              >{food.get('carbohydrates')}</strong
            >
          </li>
          <li class="list-group-item">
            Fats:&nbsp;<strong>{food.get('fats')}</strong>
          </li>
          <li class="list-group-item">
            Proteins:&nbsp;<strong>{food.get('protein')}</strong>
          </li>
        </ul>
      </div>
      <button
        hx-delete="/lunch-list-logbook/delete/{random_uuid}"
        hx-target="closest li"
        type="button"
        class="btn btn-secondary"
      > Delete
      </button>
    </div>
  </li>
   <button
    hx-get="/lunch-list-logbook/add-form"
    hx-target="this"
    hx-swap="outerHTML"
    type="button"
    class="btn btn-primary"
  >
    Add Lunch
  </button>
 
           """


###############################################DINNER#####################################
@app.route("/dinner-list-logbook")
def dinner_list_logbook():
    food_by_person = session.get("food_by_selected_person")
    selected_date = session.get("selected_date")
    dinner_for_date = [
        food
        for food in food_by_person
        if food.get("datetime").date() == selected_date
        and food.get("type").rfind("dinner") != -1
    ]

    return render_template(
        "dinner_list_logbook.html",
        date=selected_date,
        dinnerlist=dinner_for_date,
    )


@app.route("/dinner-list-logbook/delete/<string:foodid>", methods=["DELETE"])
def do_delete_dinner_to_list_logbook(foodid):
    delete_food(foodid)
    return ""


@app.route("/dinner-list-logbook/add-form")
def add_dinner_to_list_logbook():
    return render_template("add_dinner_food_form.html", foods=foods)


@app.route("/dinner-list-logbook/add", methods=["POST"])
def do_add_dinner_to_list_logbook():
    data = request.form.get("dinnerfoodselection")
    food = json.loads(data)
    random_uuid = uuid.uuid4()
    today_date = datetime.now()
    add_food(
        food,
        session["current_user"],
        "dinner",
        today_date.strftime("%Y-%m-%d %H:%M:%S"),
        random_uuid,
    )
    return f"""
             <li
    class="list-group-item d-flex justify-content-between align-items-center"
    key="{random_uuid}"
  >
    <div class="card" style="width: 18rem">
      <div class="card-header">{food.get('name')}</div>
      <div class="card-body">
        <ul class="list-group list-group-flush">
          <li class="list-group-item">
            Calories:&nbsp;<strong>{food.get('calories')}</strong>
          </li>
          <li class="list-group-item">
            Carbohydrates:&nbsp;<strong
              >{food.get('carbohydrates')}</strong
            >
          </li>
          <li class="list-group-item">
            Fats:&nbsp;<strong>{food.get('fats')}</strong>
          </li>
          <li class="list-group-item">
            Proteins:&nbsp;<strong>{food.get('protein')}</strong>
          </li>
        </ul>
      </div>
      <button
        hx-delete="/dinner-list-logbook/delete/{random_uuid}"
        hx-target="closest li"
        type="button"
        class="btn btn-secondary"
      > Delete
      </button>
    </div>
  </li>
   <button
    hx-get="/dinner-list-logbook/add-form"
    hx-target="this"
    hx-swap="outerHTML"
    type="button"
    class="btn btn-primary"
  >
    Add Dinner
  </button>
 
           """


#####################################################SNACK#####################################
@app.route("/snack-list-logbook")
def snack_list_logbook():
    food_by_person = session.get("food_by_selected_person")
    selected_date = session.get("selected_date")
    snack_for_date = [
        food
        for food in food_by_person
        if food.get("datetime").date() == selected_date
        and food.get("type").rfind("snack") != -1
    ]

    return render_template(
        "snack_list_logbook.html",
        date=selected_date,
        snacklist=snack_for_date,
    )


@app.route("/snack-list-logbook/delete/<string:foodid>", methods=["DELETE"])
def do_delete_snack_to_list_logbook(foodid):
    delete_food(foodid)
    return ""


@app.route("/snack-list-logbook/add-form")
def add_snack_to_list_logbook():
    return render_template("add_snack_food_form.html", foods=foods)


@app.route("/snack-list-logbook/add", methods=["POST"])
def do_add_snack_to_list_logbook():
    data = request.form.get("snackfoodselection")
    food = json.loads(data)
    random_uuid = uuid.uuid4()
    today_date = datetime.now()
    add_food(
        food,
        session["current_user"],
        "snack",
        today_date.strftime("%Y-%m-%d %H:%M:%S"),
        random_uuid,
    )
    return f"""
             <li
    class="list-group-item d-flex justify-content-between align-items-center"
    key="{random_uuid}"
  >
    <div class="card" style="width: 18rem">
      <div class="card-header">{food.get('name')}</div>
      <div class="card-body">
        <ul class="list-group list-group-flush">
          <li class="list-group-item">
            Calories:&nbsp;<strong>{food.get('calories')}</strong>
          </li>
          <li class="list-group-item">
            Carbohydrates:&nbsp;<strong
              >{food.get('carbohydrates')}</strong
            >
          </li>
          <li class="list-group-item">
            Fats:&nbsp;<strong>{food.get('fats')}</strong>
          </li>
          <li class="list-group-item">
            Proteins:&nbsp;<strong>{food.get('protein')}</strong>
          </li>
        </ul>
      </div>
      <button
        hx-delete="/snack-list-logbook/delete/{random_uuid}"
        hx-target="closest li"
        type="button"
        class="btn btn-secondary"
      > Delete
      </button>
    </div>
  </li>
   <button
    hx-get="/snack-list-logbook/add-form"
    hx-target="this"
    hx-swap="outerHTML"
    type="button"
    class="btn btn-primary"
  >
    Add Snack
  </button>
 
           """


################################ Weight ###########################################


@app.route("/weight-range-update")
def weight_range_update():
    value = request.args.get("weightSelected")
    return f"""
      <div id="weightOutput">
  <svg
    viewBox="0 0 240 80"
    xmlns="http://www.w3.org/2000/svg"
  >
    <style>
      /* Note that the color of the text is set with the    *
       * fill property, the color property is for HTML only */
      .weightDisplay {{
        font: italic 40px serif;
        fill:  blue;
      }}
    </style>
    <text x="0" y="55" class="weightDisplay">{value}lbs</text>
  </svg>
  <svg viewBox="0 0 200 150" width="300" height="225" xmlns="http://www.w3.org/2000/svg">
    <style>
      :root {{
        --weight: {value}; /* Change this from 0 to 300 to adjust the dial */
      }}
      .dial {{
        transform-origin: 100px 100px;
        /* Fix: Adjusted calculation to distribute weight properly across 180° */
        transform: rotate(calc(-90deg + (var(--weight) / 300 * 180deg)));
      }}
      .scale-text {{
        font: 10px sans-serif;
        fill: #444;
        text-anchor: middle;
      }}
      .scale-tick {{
        stroke: #333;
        stroke-width: 2;
      }}
      .dial-hand {{
        stroke: red;
        stroke-width: 3;
      }}
      /* Added for weight display */
      .weight-display {{
        font: bold 14px sans-serif;
        fill: #222;
        text-anchor: middle;
      }}
    </style>
    <!-- Scale Outline -->
    <circle cx="100" cy="100" r="90" fill="#f8f8f8" stroke="#aaa" stroke-width="2" />
    <path d="M10,100 A90,90 0 0,1 190,100" fill="#e0e0e0" stroke="#999" stroke-width="1" />
    <!-- Ticks and Labels (0 to 300 lbs in steps of 30) -->
    <g id="ticks">
      <g transform="rotate(-90 100 100)">
        <!-- 11 ticks from 0 to 300 (each 30 lbs = 18deg) -->
        <!-- 300 / 30 = 10 intervals → 180 / 10 = 18° apart -->
        <g transform="rotate(0 100 100)">
          <line x1="100" y1="15" x2="100" y2="25" class="scale-tick" />
          <text x="100" y="12" class="scale-text">0</text>
        </g>
        <g transform="rotate(18 100 100)">
          <line x1="100" y1="15" x2="100" y2="25" class="scale-tick" />
          <text x="100" y="12" class="scale-text">30</text>
        </g>
        <g transform="rotate(36 100 100)">
          <line x1="100" y1="15" x2="100" y2="25" class="scale-tick" />
          <text x="100" y="12" class="scale-text">60</text>
        </g>
        <g transform="rotate(54 100 100)">
          <line x1="100" y1="15" x2="100" y2="25" class="scale-tick" />
          <text x="100" y="12" class="scale-text">90</text>
        </g>
        <g transform="rotate(72 100 100)">
          <line x1="100" y1="15" x2="100" y2="25" class="scale-tick" />
          <text x="100" y="12" class="scale-text">120</text>
        </g>
        <g transform="rotate(90 100 100)">
          <line x1="100" y1="15" x2="100" y2="25" class="scale-tick" />
          <text x="100" y="12" class="scale-text">150</text>
        </g>
        <g transform="rotate(108 100 100)">
          <line x1="100" y1="15" x2="100" y2="25" class="scale-tick" />
          <text x="100" y="12" class="scale-text">180</text>
        </g>
        <g transform="rotate(126 100 100)">
          <line x1="100" y1="15" x2="100" y2="25" class="scale-tick" />
          <text x="100" y="12" class="scale-text">210</text>
        </g>
        <g transform="rotate(144 100 100)">
          <line x1="100" y1="15" x2="100" y2="25" class="scale-tick" />
          <text x="100" y="12" class="scale-text">240</text>
        </g>
        <g transform="rotate(162 100 100)">
          <line x1="100" y1="15" x2="100" y2="25" class="scale-tick" />
          <text x="100" y="12" class="scale-text">270</text>
        </g>
        <g transform="rotate(180 100 100)">
          <line x1="100" y1="15" x2="100" y2="25" class="scale-tick" />
          <text x="100" y="12" class="scale-text">300</text>
        </g>
      </g>
    </g>
    <!-- Dial Needle -->
    <line x1="100" y1="100" x2="100" y2="25" class="dial dial-hand" />
    <!-- Center Pin -->
    <circle cx="100" cy="100" r="4" fill="#000" />
    <!-- Weight Display -->
    <rect x="70" y="120" width="60" height="20" rx="3" fill="#e0e0e0" stroke="#999" />
    <text x="100" y="135" class="weight-display">
      <tspan id="weight-display-value">{value}</tspan> lbs
    </text>
  </svg>
</div>"""


@app.route("/save-current-weight")
def save_current_weight():
    random_uuid = uuid.uuid4()
    today_date = datetime.now()
    weight = {"Weight(pounds)": request.args.get("weightSelected")}
    add_weight(
        weight,
        session["current_user"],
        today_date.strftime("%Y-%m-%d"),
        random_uuid,
    )
    return "Save"


############################################## Water #########################


@app.route("/add-water-to-database")
def add_water_to_database():
    value = request.args.get("waterSelected")
    water = float(value)
    random_uuid = uuid.uuid4()
    today_date = datetime.now()
    add_water(
        {"Water(ounces)": water},
        session["current_user"],
        today_date.strftime("%Y-%m-%d"),
        random_uuid,
    )
    return '<span class="material-icons-outlined">check</span>'


@app.route("/save-total-water-comsumed-today")
def save_water_comsumed_today():
    value = request.args.get("waterSelected")
    daily_requirement = 135
    return f"""

<div id="waterOutput">
     You have consumed {value} <strong>ounces</strong>. That is on your way to getting your daily requirement of 135 <strong> ounces</stong>. 
     <br>
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 200 400"
      width="200"
      height="400"
    >
      <style>
        svg {{
          --water-level: {(float(value)/float(daily_requirement))*100}%; /* Change this value to adjust water level */
        }}

        .water {{
          fill: rgba(52, 152, 219, 0.85);
        }}

        .water-clip rect {{
          height: var(--water-level);
          y: calc(380px - var(--water-level));
          transition: height 0.3s, y 0.3s;
        }}
      </style>

      <!-- Bottle Shape for Clipping -->
      <defs>
        <clipPath id="bottleClip">
          <path
            d="M70,30 L70,10 C70,5 80,5 80,5 L120,5 C120,5 130,5 130,10 L130,30 L130,80 C130,80 150,100 150,120 L150,350 C150,370 130,380 130,380 L70,380 C70,380 50,370 50,350 L50,120 C50,100 70,80 70,80 Z"
          />
        </clipPath>
      </defs>

      <!-- Water fill (rect controlled by CSS variable) -->
      <g clip-path="url(#bottleClip)">
        <g class="water-clip">
          <rect class="water" x="50" width="100" y="0" height="380" />
        </g>
      </g>

      <!-- Bottle Body -->
      <path
        d="M70,30 L70,10 C70,5 80,5 80,5 L120,5 C120,5 130,5 130,10 L130,30 L130,80 C130,80 150,100 150,120 L150,350 C150,370 130,380 130,380 L70,380 C70,380 50,370 50,350 L50,120 C50,100 70,80 70,80 Z"
        fill="rgba(220, 230, 240, 0.7)"
        stroke="#555"
        stroke-width="2"
      />

      <!-- Bottle Cap -->
      <rect
        x="80"
        y="5"
        width="40"
        height="10"
        fill="#2980b9"
        stroke="#555"
        stroke-width="1"
      />

      <!-- Optional Highlight -->
      <path
        d="M65,40 L70,40 L70,70 C70,70 60,75 60,85 L60,100"
        stroke="rgba(255, 255, 255, 0.3)"
        stroke-width="1"
        fill="none"
      />
    </svg>
"""


################################## Exercise  ####################################
@app.route("/add-exercise-form")
def show_add_exercise_form():
    return render_template("add_exercise_form.html", workouts=workouts)


@app.route("/add-exercise-to-database", methods=["POST"])
def add_exercise_to_database():
    value = request.form.get("workoutSelected")
    exercise = {"Exercise": value, "Reps": 10, "Sets": 3}
    random_uuid = uuid.uuid4()
    today_date = datetime.now()
    add_exercise(
        exercise,
        session["current_user"],
        today_date.strftime("%Y-%m-%d"),
        random_uuid,
    )
    return render_template("add_exercise_form.html", workouts=workouts)


################################## Sleep ######################################
@app.route("/amount-slept-today")
def show_amount_slept_today():
    sleepNumber = request.args.get("sleepKeeper")
    return f"""   <div id="sleepOutput">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 300 250"
        width="300"
        height="250"
      >
        <style>
          :root {{
            --hours-slept: {sleepNumber}; /* Change this to a value between 0 and 24 */
          }}

          .label {{
            font-family: Arial, sans-serif;
            font-size: 14px;
            fill: #444;
            text-anchor: middle;
          }}

          .value {{
            font-size: 28px;
            font-weight: bold;
          }}

          .status {{
            font-size: 16px;
            font-weight: bold;
            fill: hsl(calc((var(--hours-slept) / 8) * 120), 80%, 45%);
          }}
        </style>

        <!-- Circle background -->
        <circle
          cx="150"
          cy="125"
          r="80"
          fill="#f0f0f0"
          stroke="#ccc"
          stroke-width="10"
        />

        <!-- Dynamic arc for sleep -->
        <circle
          cx="150"
          cy="125"
          r="80"
          fill="none"
          stroke="hsl(calc((var(--hours-slept) / 8) * 120), 80%, 50%)"
          stroke-width="10"
          stroke-dasharray="calc((var(--hours-slept) / 8) * 502.65) 502.65"
          stroke-linecap="round"
          transform="rotate(-90 150 125)"
        />

        <!-- Sleep duration text -->
        <text x="150" y="115" class="label value">
          <tspan id="hours-slept-text">{sleepNumber}</tspan>
          hrs
        </text>

        <!-- Recommended text -->
        <text x="150" y="145" class="label">of 8 hrs recommended</text>

        <!-- Status -->
        <text x="150" y="180" class="label status">
          <tspan id="status-text">Sleep</tspan>
        </text>
      </svg>
    </div>"""


@app.route("/save-sleep-for-today")
def save_sleep_for_today():
    value = request.args.get("sleepKeeper")
    sleep = float(value)
    random_uuid = uuid.uuid4()
    today_date = datetime.now()
    add_sleep(
        {"Sleep(hours)": sleep},
        session["current_user"],
        today_date.strftime("%Y-%m-%d"),
        random_uuid,
    )
    return "Save"


###################################################################################
@app.route("/pulse", methods=["GET"])
def get_pulse():
    return jsonify(datetime.now(timezone.utc))


if __name__ == "__main__":
    app.run(debug=True)
