from flask import render_template, redirect, url_for, flash, session, jsonify, request,make_response, g, abort
from app import app, db, lm
from .models import User, Question, QuestionType, Survey, Response, Group, SurveyQuestion, SurveyResponse, ROLE_ADMIN, ROLE_DEFAULT, GROUP_DEFAULT, ROLE_OFFICER, ROLE_INTERVIEWER, Dimensions, UserRole
from .forms import LoginForm, RegistrationForm, SurveyForm, QuestionForm, AddQuestionForm, AddUserForm, EditUserForm
from werkzeug.security import  generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from flask_login import login_user, logout_user, current_user, login_required
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons



TYPE_QUES = { 
        "QUES_AGE":1,
        "QUES_Y_N":2,
        "QUES_SCALE":3,
        "QUES_M_F":4
}

SCALE_RES = { 
        "SA":20,
        "A":5,
        "U":0,
        "D":-5,
        "SD":-20
}


REV_SCALE_RES = { 
        20:"SA",
        5:"A",
        0:"U",
        -5:"D",
        -20:"SD"
}


YN_RES = { 
        "Y":15,
        "U":0,
        "N":-15
}

REV_YN_RES = { 
        15:"Y",
        0:"U",
       -15:"N"
}



MF_RES = { 
        "M":1,
        "F":0
}

AGE_RES = { 
        "18-32":1,
        "33-48":2,
        "49-100":3
}




#==============================================
def debug(aVariable):
    print("*****************>>> Printing Variable: ",aVariable)

def active_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user.active_user == INACTIVE_USER:
            flash("Please wait for activation", category='danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.errorhandler(413)
def internal_error(error):
    db.session.rollback()
    return render_template('413.html'), 413


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/', methods=['GET', 'POST'])
def index():
    if g.user.is_authenticated:
        return redirect(url_for('main'))

    return render_template('index.html',title='CART Survey System')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if g.user is not None:
    # if g.user is not None and g.user.is_authenticated():
        # return redirect(url_for('index'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash(
                'The username or password you entered is incorrect!',
                category='danger')
            return redirect(url_for('login'))
        if user.password is None or user.password == "":
            flash(
                'The username or password you entered is incorrect!',
                category='danger')
            return redirect(url_for('login'))
        if user and check_password_hash(
                user.password,
                form.password.data) and user.is_active():
            session['remember_me'] = form.remember_me.data
            if 'remember_me' in session:
                remember_me = session['remember_me']
                session.pop('remember_me', None)
            login_user(user, remember=remember_me)
            flash('You have successfully logged in', category='success')
            return redirect(request.args.get('next') or url_for('main'))

        if user and not check_password_hash(
                user.password, form.password.data) and user.is_active():
            flash('Please check your username and password!', category='danger')
            return redirect(url_for('login'))

        if user and check_password_hash(
                user.password,
                form.password.data) and not user.is_active():
            flash("Your account needs activation!", category='warning')
            return redirect(url_for('login'))

        if user and not check_password_hash(
                user.password,
                form.password.data) and not user.is_active():
            flash("Your account needs activation!", category='warning')
            return redirect(url_for('login'))

    return render_template('login.html',
                           title='Sign In',
                           form=form)




@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('There is already a user with this email!', category='danger')
            return redirect(url_for('register'))
        user = User(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            email=form.email.data,
            password=generate_password_hash(
                form.password.data),
            user_role=ROLE_DEFAULT,
            group_id=GROUP_DEFAULT)
        db.session.add(user)
        db.session.commit()
        flash(
            'Thanks for registering. Your account will need activation.',
            category='info')
        return redirect(url_for('login'))
    return render_template(
        'register.html',
        title='Register',
        form=form,
        )


@app.route('/main', methods=['GET', 'POST'])
@login_required
def main():
    form = SurveyForm()
    if (g.user.user_role == ROLE_INTERVIEWER):
        surveys = db.session.query(Survey,Group).filter(Survey.group_id==Group.id,Survey.group_id==g.user.group_id).all()
        return render_template('dosurveys.html', surveys=surveys, title='Your Surveys')

    if (g.user.user_role == ROLE_OFFICER) or (g.user.user_role == ROLE_ADMIN):
    # surveys = Survey.query.filter_by(creator=g.user.id).all()
        surveys = db.session.query(Survey,Group).filter(Survey.group_id==Group.id, Survey.creator==g.user.id).all()
    else:
        abort(404)
    return render_template('main.html',surveys=surveys, title='Your Surveys',form=form)


@app.route('/addsurvey', methods=['POST'])
@login_required
def addsurvey():
    try:
        name = request.form['name']
        description = request.form['description']
        start_date  = request.form['start_date']
        end_date  = request.form['end_date']
        group_id = request.form['group_id']
        debug(group_id)

        survey = Survey(name=name, description=description, start_date=start_date, end_date=end_date,updated=datetime.datetime.now(),creator=g.user.id,group_id=group_id)
        db.session.add(survey)
        db.session.commit()
        flash('Survey successfully created',category='success')
        return redirect(url_for('main'))

    except Exception as e:
        print(e)

    return "<b> You shouldn't have reached here!'</b>"


@app.route('/addquestion', methods=['POST'])
@login_required
def addquestion():
    try:
        question_title = request.form['question_title']
        dimension = request.form['dimension']
        question_type = request.form['question_type']
        question = Question(question_title=question_title, question_type=question_type, dimension=dimension,create_officer=g.user.id, updated=datetime.datetime.now())
        
        db.session.add(question)
        db.session.commit()
        flash('Question successfully created',category='success')
        return redirect(url_for('questions'))

    except Exception as e:
        print(e)

    return "<b> You shouldn't have reached here!'</b>"

   

@app.route('/addquestionstosurvey', methods=['POST'])
@login_required
def addquestionstosurvey():
    try:
        if request.method == 'POST':
            sid = request.form['sid']
            sq = request.form.getlist('surveyquestions')
            for s in sq:
                question = SurveyQuestion(survey=sid,question=int(s))
                db.session.add(question)
                db.session.commit()
            flash('Questions successfully added to survey', category='success')
            return redirect(url_for('preview',id=sid))
    except Exception as e:
        print(e)


    return "<b> You shouldn't have reached here!'</b>"





@app.route('/questions', methods=['GET', 'POST'])
@login_required
def questions():
    form = QuestionForm()

    if (g.user.user_role == ROLE_OFFICER) or (g.user.user_role == ROLE_ADMIN):
        questions = Question.query.filter_by(create_officer=g.user.id).all()
    else:
        abort(404)
    return render_template('questions.html',questions=questions, form=form, title='Your Questions')

@app.route('/editquestion/<id>', methods=['GET', 'POST'])
@login_required
def editquestion(id):
    form = QuestionForm()
    if (g.user.user_role == ROLE_OFFICER) or (g.user.user_role == ROLE_ADMIN):
        question = Question.query.get_or_404(id)
        if form.validate_on_submit():

            question_title = request.form['question_title']
            question_type = request.form['question_type']
            dimension = request.form['dimension']

            question.question_title = question_title
            question.question_type = int(question_type)
            question.dimension = int(dimension)
            question.updated = datetime.datetime.now()

            db.session.add(question)
            db.session.commit()
            flash('Question was successfully updated',category='success')
            return redirect(url_for('questions'))
        else:
            form.question_title.data = question.question_title
            form.question_type.data = str(question.question_type)
            form.dimension.data = str(question.dimension)
    else:
        abort(404)
    return render_template('editquestion.html',question=question, id=id, form=form, title='Edit Question')






@app.route('/preview/<id>', methods=['GET','POST'])
@login_required
def preview(id):
    if (g.user.user_role == ROLE_OFFICER) or (g.user.user_role == ROLE_ADMIN):
        survey = Survey.query.filter_by(id=int(id)).first()
        surveyq = db.session.query(Survey,Question,SurveyQuestion).filter(Survey.id==SurveyQuestion.survey,Question.id == SurveyQuestion.question,Survey.id==id).all()

        # nsurveyq = db.session.query(Survey,Question,SurveyQuestion).filter(Survey.id==SurveyQuestion.survey,Question.id == SurveyQuestion.question,Survey.id!=id).all()
        sub_msurvey = db.session.query(SurveyQuestion.question).filter_by(survey=int(id))
        nsurveyq = db.session.query(Question).filter(Question.id.notin_(sub_msurvey)).all()
        dimensions = Dimensions.query.all()
        # msurvey = db.session.query(Question).outerjoin(SurveyQuestion, (SurveyQuestion.question==Question.id and SurveyQuestion.question == None)).all()
        # debug(msurvey)
        # nsurvey = null
        # for m in msurvey

    else:
        abort(404)
    return render_template('preview.html', surveyq=surveyq,survey=survey, nsurveyq=nsurveyq, dimensions=dimensions, title='Preview Survey')




@app.route('/administer/<id>', methods=['GET','POST'])
@login_required
def administer(id):
    if (g.user.user_role == ROLE_INTERVIEWER):
        survey = Survey.query.filter_by(id=int(id)).first()
        surveyq = db.session.query(Survey,Question,SurveyQuestion).filter(Survey.id==SurveyQuestion.survey,Question.id == SurveyQuestion.question,Survey.id==id).all()
    else:
        abort(404)
    return render_template('administer.html', surveyq=surveyq,survey=survey, title='Administer Survey')



@app.route('/savesurvey',methods=['POST'])
@login_required
def savesurvey():
    sid = request.form["surveyid"] 
    lat = round(float(request.form["lat"]), 6)
    lon = round(float(request.form["lon"]), 6)

    sr = SurveyResponse(survey_id=int(sid),interviewer=g.user.id,latitude=lat,longitude=lon, completed=datetime.datetime.now())
    db.session.add(sr)
    db.session.flush()
    db.session.commit()
    # debug(sr.id)
    for k,v in request.form.items():
        if k=="surveyid" or k=="lat" or k=="lon":
            continue
        r = Response(survey_response_id=sr.id,question=k,response=v)
        db.session.add(r)
        db.session.commit()
    flash('The survey response was successfully saved!', category='success')
    return redirect(url_for('administer',id=sid))








@app.route('/statistics/<id>', methods=['GET'])
@login_required
def statistics(id):
    sSurvey = Survey.query.get_or_404(id)
    #THIS NEED TO FIX
    maximum = {
            3: 20,
            2: 15
            }

    dimensions = Dimensions.query.all()
    dimensionsDict = {}
    dimensionsMaxDict = {}
    finalDimensionsMaxDict = {}
    for d in dimensions:
        dimensionsDict[d.id] = {} 
        dimensionsMaxDict[d.id] = {} 
        finalDimensionsMaxDict[d.id] = 0

    # debug(dimensionsDict)
    allSurveys = SurveyResponse.query.filter_by(survey_id=int(id))
    surveyPlots = allSurveys.all()
    nResponses = allSurveys.count()
    if not nResponses:
        flash('There are no responses to perform any statistics', category='danger')
        return redirect(url_for('main'))
    nQuestions = SurveyQuestion.query.filter_by(survey=int(id)).count()
    allQuestions = db.session.query(Question, SurveyQuestion).filter(Question.id==SurveyQuestion.question, SurveyQuestion.survey==int(id)).all()
    stats = {}
    qtype = {}
    qtype_updated = {}
    readiness_question = {}
    num_response_question = {}
    sDict = {}
    yDict = {}
    # dimensionsQuestions = {}
    for q in allQuestions:
        dimensionsDict[q.Question.dimension][q.Question.id] = 0
        # dimensionsDict[q.Question.dimension].append(q.Question.id)
        response = Response.query.filter_by(question=q.Question.id).all()
        stats[q.Question.id] = 0
        qtype[q.Question.id] = q.Question.question_type
        # ===== START  section to calculate num of responses 
        if q.Question.question_type == 3:
            sDict[q.Question.id] = {"SA":0, "A":0, "U":0,"D":0,"SD":0}
        if q.Question.question_type == 2:
            yDict[q.Question.id] = {"Y":0, "U":0, "N":0}
        # ===== End section to calculate num of responses 
        for r in response:
            stats[q.Question.id] = stats[q.Question.id] + r.response 
            # ===== START  section to calculate num of responses 
            if q.Question.question_type == 3:
                sDict[q.Question.id][REV_SCALE_RES[r.response]] += 1 

            if q.Question.question_type == 2:
                yDict[q.Question.id][REV_YN_RES[r.response]] += 1 
            # ===== End section to calculate num of responses 
    # debug(yDict)

        # changing qtype to have max values
    for k,v in qtype.items():
        qtype_updated[k] = maximum[v]*nResponses


    # building dimension totals of the form {1: {1:0, 2:0}} to eg. {1: {1:35, 2:40}}
    # also building max dimensions of the form {1: {1:0, 2:0}} to eg. {1: {1:80, 2:80}}
    for k,v in dimensionsDict.items():
         r = dimensionsDict[k]
         for i in r:
             dimensionsDict[k][i] = stats[i]
             dimensionsMaxDict[k][i] = qtype_updated[i]
    # debug(stats)
    # debug(dimensionsDict)

    #summing the values for each dimension
    sumDimensionsDict = {k:sum(v.values()) for k,v in dimensionsDict.items()}
    debug(sumDimensionsDict)
    debug(dimensionsMaxDict)

    # summing the max values for the dimensions 
    sumDimensionsMaxDict = {k:sum(v.values()) for k,v in dimensionsMaxDict.items()}
    debug(sumDimensionsMaxDict)

    # calculation of final dimensions readiness values
    for k in finalDimensionsMaxDict:
        finalDimensionsMaxDict[k] = int(round((sumDimensionsDict[k]/sumDimensionsMaxDict[k])*100,0))
    debug(finalDimensionsMaxDict)

    for k, v in stats.items():
        readiness_question[k] = int(round((v/qtype_updated[k]) * 100, 0))

    # print(stats)
    # print(qtype)
    # print(qtype_updated)
    # print(readiness_question)
    sum_all_readiness = sum([v for k, v in stats.items()])
    total_max_readiness = sum([v for k,v in qtype_updated.items()])
    total_readiness =  round((sum_all_readiness/total_max_readiness)* 100, 0)
    # print(readiness_question)

    # ==========================GOOGLE MAPS============================
    # creating a map in the view
    markersList = []
    for sp in surveyPlots:
        if(sp.latitude==0 or sp.longitude == 0):
            continue
        lDict={}
        lDict['icon'] = 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
        lDict['lat'] = str(sp.latitude)
        lDict['lng'] = str(sp.longitude)
        lDict['infobox'] ='lat:'+str(sp.latitude)+' lon:'+ str(sp.longitude)
        markersList.append(lDict)

    print(markersList)
    sndmap = Map(
        identifier="sndmap",
        lat=18.115517,
        lng=-77.276003,
        zoom=9,
        style=(
            "height:500px;"
            "width:800px;"
            ),
        markers = markersList 
        # markers=[
          # {
             # 'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             # 'lat': 18.016666,
             # 'lng': -76.766636,
             # 'infobox': "<b>Hello World</b>"
          # },
          # {
             # 'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
             # 'lat': 18.01248,
             # 'lng': -76.79928,
             # 'infobox': "<b>Hello World from other place</b>"
          # }
        # ]
    )

    print("-------------------------------------------")
    print(request.path)
    return render_template('statistics.html', title='Statistics', nResponses=nResponses,
            readiness_question=readiness_question,total_readiness=total_readiness,
            allQuestions=allQuestions,yDict=yDict,sDict=sDict,dimensions=dimensions,
            finalDimensionsMaxDict=finalDimensionsMaxDict,sndmap=sndmap,sSurvey=sSurvey)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have successfully logged out!', category='success')
    return redirect(url_for('login'))

@app.route('/get')
def get():
    return jsonify({"message":"Welcome to Flutter"})



@app.route('/manageusers',methods=['GET','POST'])
@login_required
def manageusers():
    form = AddUserForm()
    users = User.query.all()
    groups = Group.query.all()
    uRoles = UserRole.query.all()
    groupsDict = {}
    rolesDict = {}
    for group in groups:
        groupsDict[group.id] =  group.name

    for role in uRoles:
        rolesDict[role.id] =  role.name

    return render_template('manageusers.html', title="Manage Users", users=users, form=form, groupsDict=groupsDict, rolesDict=rolesDict)



@app.route('/saveuser',methods=['POST'])
@login_required
def saveuser():
    firstname = request.form["firstname"] 
    lastname = request.form["lastname"] 
    email = request.form["email"] 
    password = request.form["password"] 
    user_role = request.form["user_role"] 
    group_id = request.form["group_id"] 
    active_user = request.form["active_user"]
    user = User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=generate_password_hash(
                password),
            user_role=int(user_role),
            group_id=int(group_id),
            active_user=int(active_user))
    db.session.add(user)
    db.session.commit()
    flash('The user was successfully saved!', category='success')
    return redirect(url_for('manageusers'))

@app.route('/edituser/<int:id>',methods=['GET','POST'])
@login_required
def edituser(id):
    title='Edit User'
    user = User.query.get_or_404(id)
    if not user:
        abort(404)
    form = EditUserForm()
    if form.validate_on_submit():

        firstname = request.form["firstname"] 
        lastname = request.form["lastname"] 
        user_role = request.form["user_role"] 
        group_id = request.form["group_id"] 
        active_user = request.form["active_user"]
    
        user.firstname = firstname
        user.lastname = lastname
        user.user_role = int(user_role)
        user.group_id = int(group_id)
        user.active_user = int(active_user)
        db.session.add(user)
        db.session.commit()
        flash('User '+firstname + ' '+ lastname +' was edited successfully',category='success')
        return redirect(url_for('manageusers'))
    else:
        form.firstname.data = user.firstname
        form.lastname.data = user.lastname
        form.user_role.data = str(user.user_role)
        form.group_id.data = str(user.group_id)
        form.active_user.data = "1" if user.active_user else "0"

    return render_template('edituser.html',form=form,title=title,id=user.id,user=user)


#==============================================

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
 

@app.route('/registera',methods=['POST'])
def registera():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    user = User(firstname=data['firstname'],lastname=data['lastname'],email=data['email'],password=hashed_password,user_role=1,group_id=1)
    db.session.add(user)
    db.session.commit()
    # response.headers.add('Access-Control-Allow-Origin', '*')
    return jsonify({'Message':'The user was created.'}) 




@app.route('/users',methods=['GET'])
# @token_required
def get_users():
# def get_users(current_user):

    # =========after decorator=============
    # if current_user.admin != ROLE_ADMIN :
        # return jsonify({'Message':'Sorry, function not permitted!'})
    #=========end after decorator==========


    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        # user_data["id"] = user.id
        user_data["firstname"] = user.firstname
        # user_data["lastname"] = user.lastname
        # user_data["email"] = user.email
        # user_data["user_role"] = user.user_role
        output.append(user_data)
    return jsonify(output) 



@app.route('/user')
@token_required
def user(current_user):
    user_data = {}
    user_data["id"] = current_user.id
    user_data["firstname"] = current_user.firstname
    user_data["lastname"] = current_user.lastname
    user_data["email"] = current_user.email
    user_data["user_role"] = current_user.user_role

    return jsonify(user_data)


@app.route('/surveys')
@token_required
def surveys(current_user):

    user =  User.query.filter_by(id=current_user.id).first()
    surveys = Survey.query.filter_by(group_id=user.group_id).all()
    survey_list = []
    for s in surveys:
        survey_dict = {}
        survey_dict["id"] = s.id
        survey_dict["name"] = s.name
        survey_dict["description"] = s.description
        survey_list.append(survey_dict)
    return jsonify(survey_list)


@app.route('/survey',methods=['POST'])
@token_required
def survey(current_user):
    data = request.get_json()
    sid = data["data"]["sid"]
    surveys = Survey.query.filter_by(id=int(sid),group_id=current_user.group_id).all()
    questions_survey = db.session.query(Question, SurveyQuestion).filter(Question.id==SurveyQuestion.question).all()
    quest_dict = {}
    for q in questions_survey:
        quest_dict[q.Question.id] =  q.Question.question_title

    return jsonify(quest_dict)



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
    user_data["user_role"] = user.user_role

    return jsonify({"user":user_data})


@app.route('/user/<user_id>',methods=['PUT'])
@token_required
# def promote_user(user_id):
def promote_user(current_user,user_id):

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'Message':'User does not exists!'})
    user.user_role = ROLE_ADMIN
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


@app.route('/authlogin1',methods=['POST'])
def authlogin1():
    auth = request.authorization
    debug(auth)
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


def decodeAuthToken(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithm='HS256')
        return payload
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Login please'
    except jwt.InvalidTokenError:
        return 'Nice try, invalid token. Login please'




@app.route('/authlogin', methods=['POST'])
def loginAndGenerateToken():
    # valid_user_1 = {'username': "test_user_1", 'password': 'Happy123'}
    # valid_user_2 = {'username': 'test_admin', 'password': 'LessHappy123'}

    req_json = request.get_json()
    # print("Request >>>")
    print(request)
    # print("json >>>")
    print(req_json)
    email = req_json['email']
    # print(email)
    password = req_json['password']
    # print(password)

    try:
        user = User.query.filter_by(email=email).first()

        if check_password_hash(user.password,password):
            if (user.user_role == ROLE_ADMIN):
                token = encodeAuthToken(email, ['admin'])
            else:
                token = encodeAuthToken(email)

        user_data = {}
        user_data["id"] = user.id
        user_data["firstname"] = user.firstname
        user_data["lastname"] = user.lastname
        user_data["email"] = user.email
        user_data["user_role"] = user.user_role

        # if username == valid_user_1['username'] and password == valid_user_1['password']:
            # token = encodeAuthToken(1)

        # if username == valid_user_2['username'] and password == valid_user_2['password']:

            # token = encodeAuthToken(2, ['admin'])

        print(token)
        return jsonify({
            'status': 'success',
            'user': user_data,
            'auth_token': token.decode('UTF-8')
            # 'auth_token': token
        })
    except Exception as e:
        return jsonify({
            'status': 'Failure',
            'error': str(e)
        })


@app.route('/create_question',methods=['POST'])
@token_required
def create_question(current_user):
    data = request.get_json()
    question = data["question"]
    question_type = data["question_type"]

    q = Question(question_title=question,question_type=TYPE_QUES[question_type], officer=current_user.id)
    db.session.add(q)
    db.session.commit()

    return jsonify({'Message':'The question was created.'}) 


@app.route('/rest_surveys', methods=['GET', 'POST'])
@token_required
def rest_surveys(current_user):
# def rest_surveys():
    ruserid = 3
    rgroupid = 1
    role = 2
    result = []
    dimension_dict = {}
    # surveys = db.session.query(Survey,Group).filter(Survey.group_id==Group.id,Survey.group_id==1).all()
    surveys = db.session.query(Survey,Group).filter(Survey.group_id==Group.id,Survey.group_id==current_user.group_id).all()
    dimensions = Dimensions.query.all()
    for dimension in dimensions:
        dimension_dict[dimension.id] = dimension.name
    for s in surveys:
        debug(s.Survey.name)
        tempList = []
        sq = db.session.query(SurveyQuestion, Question).filter(SurveyQuestion.question==Question.id, SurveyQuestion.survey==s.Survey.id).all()
        for q in sq:
            temp = {}
            temp["id"] = q.Question.id
            temp["title"] = q.Question.question_title
            temp["dimension"] = dimension_dict[q.Question.dimension]
            temp["type"] = q.Question.question_type
            tempList.append(temp)
        sDict = {}
        sDict["id"] = s.Survey.id
        sDict["name"] = s.Survey.name
        sDict["description"] = s.Survey.description
        sDict["questions"] = tempList
        result.append(sDict)
    return jsonify(result) 

@app.route('/rest_save_survey',methods=['POST'])
@token_required
def restsavesurvey(current_user):

    req_json = request.get_json()

    sid = req_json["sid"] 
    uid = req_json["uid"] 
    lat = round(float(req_json["lat"]), 6)
    lon = round(float(req_json["lon"]), 6)

    sr = SurveyResponse(survey_id=int(sid),interviewer=int(uid),latitude=lat,longitude=lon, completed=datetime.datetime.now())
    db.session.add(sr)
    db.session.flush()
    db.session.commit()
    for k,v in req_json.items():
        if k=="sid" or k=="lat" or k=="lon" or k=="uid":
            continue
        r = Response(survey_response_id=sr.id,question=k,response=v)
        db.session.add(r)
        db.session.commit()
    return jsonify({"message":"Sucessfully saved survey responses"}) 






