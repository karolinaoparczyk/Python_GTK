First meet the requirements listed in requirements.txt.

Create database named "fitness"

Load data to database:
mongorestore --db fitness --collection workouts workouts.bson
mongorestore --db fitness --collection exercises exercises.bson

Then run

python server.py

and in another terminal

python ipm-p1.py

If this is your first time opening the app, run

python ipm-p1.py 1

which will update database
