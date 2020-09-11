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
    # response.headers.add('Access-Control-Allow-Origin', '*')
    return jsonify({'Message':'The user was created.'}) 


@app.route('/users',methods=['GET'])
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



@app.route('/user')
@token_required
def user(current_user):
    user_data = {}
    user_data["id"] = current_user.id
    user_data["firstname"] = current_user.firstname
    user_data["lastname"] = current_user.lastname
    user_data["email"] = current_user.email
    user_data["admin"] = current_user.admin

    return jsonify(user_data)




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


@app.route('/authlogin1')
def authlogin1():
    auth = request.authorization
    print(auth)
    if not auth or not auth.username or not auth.password:
        return make_response('User verification failed', 401, {'WWW-Authenticate':'Basic realm="Login Required!"'}) 
    
    user = User.query.filter_by(email=auth.username).first()

    if not user:
        return make_response('User verification failed', 401, {'WWW-Authenticate':'Basic realm="Login Required!"'}) 

    if check_password_hash(user.password,auth.password):
        token = jwt.encode({'email':user.email,'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=30)},app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('User verification failed', 401, {'WWW-Authenticate':'Basic realm="Login Required!"'}) 



def encodeAuthToken(email, groups=[]):
    try:
        admin = True if 'admin' in groups else False

        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'email': email,
            'admin': admin
        }
        token = jwt.encode(payload, app.config['SECRET_KEY'])
        return token
    except Exception as e:
        print(e)
        return e



@app.route('/authlogin', methods=['POST'])
def loginAndGenerateToken():
    # valid_user_1 = {'username': "test_user_1", 'password': 'Happy123'}
    # valid_user_2 = {'username': 'test_admin', 'password': 'LessHappy123'}

    req_json = request.get_json()
    print(req_json)
    email = req_json['email']
    print(email)
    password = req_json['password']
    print(password)

    try:
        user = User.query.filter_by(email=email).first()

        if check_password_hash(user.password,password):
            if user.admin:
                token = encodeAuthToken(email, ['admin'])
            else:
                token = encodeAuthToken(email)

        user_data = {}
        user_data["id"] = user.id
        user_data["firstname"] = user.firstname
        user_data["lastname"] = user.lastname
        user_data["email"] = user.email
        user_data["admin"] = user.admin



        # if username == valid_user_1['username'] and password == valid_user_1['password']:
            # token = encodeAuthToken(1)

        # if username == valid_user_2['username'] and password == valid_user_2['password']:

            # token = encodeAuthToken(2, ['admin'])

        print(token)
        return jsonify({
            'status': 'success',
            'user': user_data,
            'auth_token': token.decode('UTF-8')
        })
    except Exception as e:
        return jsonify({
            'status': 'Failure',
            'error': str(e)
        })








