from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)

@api.route('/signup', methods=['POST'])
def signup():
    email = request.json.get("email")
    password = request.json.get("password")

    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    user_query = User.query.filter_by(email=email).first()
    if user_query is not None:
        return jsonify({"msg": "Email already exists."}), 401
    
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created"}), 200

@api.route('/login', methods=['POST'])
def user_login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()
    if user is None or user.password != password:
        return jsonify({"msg": "Bad username or password"}), 401


    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user_id": user.id}), 200

@api.route("/protected", methods=["GET"])
@jwt_required()
def protected():

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    return jsonify({"id": user.id, "email": user.email}), 200