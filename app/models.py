from app import db

ROLE_INACTIVE = 0
ROLE_USER = 1
ROLE_INTERVIEWER = 2
ROLE_OFFICER =  3
ROLER_ADMIN =  4


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50),unique=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(140),nullable=False)
    confirmationid = db.Column(db.String(140))
    admin = db.Column(db.Boolean,default=False)
    active_user = db.Column(db.Boolean,default=False)
    interviewer_user = db.Column(db.Boolean,default=False)
    officer_user = db.Column(db.Boolean,default=False)
    avatar = db.Column(db.String(1000))

    #TODO: Problem here
    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active_user == True

    def is_admin(self):
        return self.admin == True

    def is_interviewer(self):
        return self.interviewer_user == True

    def get_id(self):
        return str(self.id)

    def is_anonymous(self):
        return False

    def __repr__(self):
        return '<User %r>' % (self.email)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(100), nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_type = db.Column(db.Integer, nullable=False)


class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interviewer = db.Column(db.Integer, db.ForeignKey('user.id'))
    question = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    response = db.Column(db.Numeric, nullable=False)

