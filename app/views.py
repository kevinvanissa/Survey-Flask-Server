from flask import render_template, redirect, url_for, flash, session, jsonify, request,make_response, g
from app import app, db
from .models import User, Question, Survey
from werkzeug.security import  generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'Message': 'Missing Token!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(email=data['email']).first()
            g.user = current_user
            # print(g.user.admin)
            # print(current_user.admin)
        except Exception as e:
            print(e)
            return jsonify({'Message': 'Invalid Token!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# def admin_required(f):
    # @wraps(f)
    # def decorated(*args, **kwargs):
            # return jsonify({'Message':'Sorry, function not permitted!'})
        # return f(*args,**kwargs)
    # return decorated
 

@app.route('/register',methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    user = User(firstname=data['firstname'],lastname=data['lastname'],email=data['email'],password=hashed_password,admin=False)
    db.session.add(user)
    db.session.commit()
    return jsonify({'Message':'The user was created.'}) 


@app.route('/user',methods=['GET'])
@token_required
# def get_users():
def get_users(current_user):

    # =========after decorator=============
    if not current_user.admin:
        return jsonify({'Message':'Sorry, function not permitted!'})
    #=========end after decorator==========


    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data["id"] = user.id
        user_data["firstname"] = user.firstname
        user_data["lastname"] = user.lastname
        user_data["email"] = user.email
        user_data["admin"] = user.admin
        output.append(user_data)
    return jsonify({'users':output}) 


@app.route('/user/<user_id>',methods=['GET'])
@token_required
# def get_one_user(user_id):
def get_one_user(current_user,user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'Message':'User does not exists!'})

    user_data = {}
    user_data["id"] = user.id
    user_data["firstname"] = user.firstname
    user_data["lastname"] = user.lastname
    user_data["email"] = user.email
    user_data["admin"] = user.admin

    return jsonify({"user":user_data})


@app.route('/user/<user_id>',methods=['PUT'])
@token_required
# def promote_user(user_id):
def promote_user(current_user,user_id):

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'Message':'User does not exists!'})
    user.admin = True
    db.session.commit()

    return jsonify({'Message':'The user is now promoted to admin!'})


@app.route('/user/<user_id>',methods=['DELETE'])
@token_required
# def delete_user(user_id):
def delete_user(current_user,user_id):

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'Message':'User does not exists!'})
    db.session.delete(user)
    db.session.commit()
 
    return jsonify({'Message':'The user %s was deleted!' % user.email})


@app.route('/authlogin')
def authlogin():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('User verification failed', 401, {'WWW-Authenticate':'Basic realm="Login Required!"'}) 
    
    user = User.query.filter_by(email=auth.username).first()

    if not user:
        return make_response('User verification failed', 401, {'WWW-Authenticate':'Basic realm="Login Required!"'}) 

    if check_password_hash(user.password,auth.password):
        token = jwt.encode({'email':user.email,'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=30)},app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('User verification failed', 401, {'WWW-Authenticate':'Basic realm="Login Required!"'}) 
