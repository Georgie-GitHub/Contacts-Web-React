from flask import request,jsonify
from config import app, db
from models import Contact
import re

#Checks for valid email
def ends_with_email(string):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.search(email_pattern + r'$', string) is None

#Accept new contacts
@app.route("/contacts",methods = ["GET"])
def get_contacts():
    contacts = Contact.query.all()
    json_contacts = list(map(lambda x: x.to_json(),contacts))
    return jsonify({"contacts": json_contacts})

#Create new contacts
@app.route("/create_contact",methods = ["POST"])
def create_contact():
    first_name = request.json.get("firstName")
    last_name = request.json.get("lastName")
    email = request.json.get("email")

    if not first_name or not last_name or not email:
        return (
            jsonify({"message":"You must include a first name, last name and email"}),
            400,
        )
    
    existing_contact = Contact.query.filter_by(first_name = first_name,last_name=last_name,email=email).first()
    if existing_contact:
        return jsonify({"message":"Contact already exists"}),400
    if ends_with_email(email):
        return jsonify({"message":"Invalid email"}),400

    new_contact = Contact(first_name = first_name,last_name=last_name,email=email)
    try:
        db.session.add(new_contact)
        db.session.commit()
    except Exception as e:
        return jsonify({"message":str(e)}),400

    return jsonify({"message":"User created!"}),201

#Update existing contact
@app.route("/update_contact/<int:user_id>",methods = ["PATCH"])
def update_contact(user_id):
    contact = Contact.query.get(user_id)

    if not contact:
        return jsonify({"message":"User not found"}),404
    
    data = request.json
    contact.first_name = data.get("firstName", contact.first_name)
    contact.last_name = data.get("lastName", contact.last_name)
    contact.email = data.get("email", contact.email)
    
    db.session.commit()

    return jsonify({"message":"User updated."}),200

#Delete existing contact
@app.route("/delete_contact/<int:user_id>",methods=["DELETE"])
def delete_contact(user_id):
    contact = Contact.query.get(user_id)

    if not contact:
        return jsonify({"message":"User not found"}),404
    
    db.session.delete(contact)
    db.session.commit()

    return jsonify({"message":"User deleted"}),200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug = True)