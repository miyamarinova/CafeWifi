import sqlalchemy.exc
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
import os

app = Flask(__name__)



##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True)
    map_url = db.Column(db.String(500))
    img_url = db.Column(db.String(500))
    location = db.Column(db.String(250))
    seats = db.Column(db.String(250))
    has_toilet = db.Column(db.Boolean)
    has_wifi = db.Column(db.Boolean)
    has_sockets = db.Column(db.Boolean)
    can_take_calls = db.Column(db.Boolean)
    coffee_price = db.Column(db.String(250))

    def to_dict(self):
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            #Create a new dictionary entry; where the key is the name of the column and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random", methods=["GET"])
def random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafes)
    print(all_cafes)
    return jsonify(cafe={
        "id":random_cafe.id,
        "name":random_cafe.name,
        "map_url":random_cafe.map_url,
        "img_url":random_cafe.img_url,
        "location":random_cafe.location,
        "seats":random_cafe.seats,
        "has_toilet":random_cafe.has_toilet,
        "has_wifi":random_cafe.has_wifi,
        "has_sockets":random_cafe.has_sockets,
        "can_take_calls":random_cafe.can_take_calls,
        "coffee_price":random_cafe.coffee_price,
    })
#Serialising database row Object to JSON by first converting to dictionary

@app.route("/all")
def all():
    return jsonify(cafes=[cafe.to_dict() for cafe in db.session.query(Cafe).all()])

@app.route("/search", methods=["GET"])
def search_cafes():
    requested_cafe = request.args.get("loc")
    for cafe in Cafe.query.all():
        if cafe.location == requested_cafe:
            return jsonify(cafe=cafe.to_dict())
    return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


@app.route("/add", methods=["POST"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form["name"],
        map_url=request.form["map_url"],
        img_url=request.form["img_url"],
        location=request.form["location"],
        seats=request.form["seats"],
        has_toilet=bool(request.form["has_toilet"]),
        has_wifi=bool(request.form["has_wifi"]),
        has_sockets=bool(request.form["has_sockets"]),
        can_take_calls=bool(request.form["can_take_calls"]),
        coffee_price=request.form["coffee_price"],
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={
        "success": "Successfully added the new cafe."
    })


@app.route("/update-price/<int:cafe_id>", methods=['PATCH'])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    for cafe in Cafe.query.all():
        if cafe:
            cafe.coffee_price = new_price
            db.session.commit()
            return jsonify(response={"success": "Successfully updated the price."})
        else:
            return jsonify(response={"error": {"Not Found": "Sorry, a cafe with that id was not found in the database."}})

@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    cafe = db.session.query(Cafe).get(cafe_id)
    if api_key == "TopSecretAPIKey":
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."})
        else:
            return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."})
    else:
        return jsonify(error={"error":{"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}})



if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
