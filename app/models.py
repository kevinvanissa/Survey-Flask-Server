from app import db

ROLE_DEFAULT = 1
ROLE_INTERVIEWER = 2
ROLE_OFFICER =  3
ROLE_ADMIN =  4
GROUP_DEFAULT = 9

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)


class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)

class RolePermission(db.Model):
    user_role_id = db.Column(db.Integer, db.ForeignKey('user_role.id'),primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50),unique=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(140),nullable=False)
    confirmationid = db.Column(db.String(140))
    user_role = db.Column(db.Integer,db.ForeignKey('user_role.id'))
    group_id = db.Column(db.Integer,db.ForeignKey('group.id'))
    active_user = db.Column(db.Boolean,default=False)
    avatar = db.Column(db.String(1000))
    # surveys = db.relationship('Survey', backref="creator", lazy=False)

    #TODO: Problem here
    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active_user == True

    def is_admin(self):
        return self.user_type == 4

    def is_interviewer(self):
        return self.user_type == 2

    def is_officer(self):
        return self.user_type  == 3

    def get_id(self):
        return str(self.id)

    def is_anonymous(self):
        return False

    def __repr__(self):
        return '<User %r>' % (self.email)

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    updated = db.Column(db.DateTime)
    creator = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    # questions = db.relationship('Question', backref="survey", lazy=False)
    #TODO: create title and description fields and possible start and end date


class Dimensions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)

class QuestionType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(100), nullable=False)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_title = db.Column(db.String(200), nullable=False)
    dimension = db.Column(db.Integer, db.ForeignKey('dimensions.id'))
    question_type = db.Column(db.Integer, db.ForeignKey('question_type.id'))
    create_officer = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated = db.Column(db.DateTime)


class SurveyQuestion(db.Model):
    survey = db.Column(db.Integer, db.ForeignKey('survey.id'),nullable=False,primary_key=True)
    question = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False,primary_key=True)

class SurveyResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))
    interviewer = db.Column(db.Integer, db.ForeignKey('user.id'))
    latitude = db.Column(db.Numeric(10,6))
    longitude = db.Column(db.Numeric(10,6))
    completed = db.Column(db.DateTime)


class Response(db.Model):
    survey_response_id = db.Column(db.Integer, db.ForeignKey('survey_response.id'), primary_key=True)
    question = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    response = db.Column(db.Integer, nullable=False)

