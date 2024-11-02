from flask import Flask
from flask_migrate import Migrate
from flask import request, jsonify, session
from models import db, User, Workout
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

API_TOKEN = os.getenv("API_TOKEN")

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:9184@localhost:5432/fitdatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = API_TOKEN
db.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def home():
    return 'Welcome to the Fitness Tracker API'

@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    new_user = User(username, password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'You have successfully been registered'})

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['user_id'] = user.id
        return jsonify({'message': 'Successfully logged in'})
    return jsonify({'message': 'User not found, Register First'})

@app.route('/add_workout', methods=['POST'])
def add_workout():
    exercise = request.json['exercise']
    duration = request.json['duration(min)']
    user_id = session['user_id']
    new_workout = Workout(user_id, exercise, duration)
    db.session.add(new_workout)
    db.session.commit()
    return jsonify({'message': 'Workout added successfully'})

@app.route('/workouts', methods=['GET'])
def workouts():
    workout = Workout.query.filter_by(user_id=session['user_id']).all()
    all_workouts = []
    for i in workout:
        all = {'id': i.id, 'exercise': i.exercise, 'duration(min)': i.duration}
        all_workouts.append(all)
    return jsonify(all_workouts)

@app.route('/progress', methods=['GET'])
def progress():
    # Total workout
    workout = Workout.query.with_entities(Workout.exercise).filter_by(user_id=session['user_id']).all()
    total_workout = ''
    for w in workout:
        total_workout = total_workout + ',' + w[0]
    # Total duration
    time = Workout.query.with_entities(Workout.duration).filter_by(user_id=session['user_id']).all()
    total_duration = 0
    for t in time:
        total_duration = total_duration + t[0]
    # Final Progress
    progress = {'total_workout': total_workout, 'total_duration(min)': total_duration}
    return jsonify(progress)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)