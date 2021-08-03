from app import db
from .models import User, Group, QuestionType, Question, Dimensions, UserRole
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, SelectField, TextAreaField, HiddenField, IntegerField, FormField, PasswordField, SelectMultipleField, FileField, DateField, DecimalField, validators,DateField
from wtforms.validators import Required, Length, Email, EqualTo, ValidationError


STATUS = [
    ("1", "YES"),
    ("0", "NO")
]

class LoginForm(FlaskForm):
    email = TextField('email', [Required(), Email()])
    password = PasswordField('password', [Required()])
    remember_me = BooleanField('remember_me', default=False)


class RegistrationForm(FlaskForm):
    firstname = TextField('firstname', [Required()])
    lastname = TextField('lastname', [Required()])
    email = TextField('email', [Required(), Email()])
    password = PasswordField('password', [Required()])
    confirm = PasswordField('confirmpassword', [
        Required(),
        EqualTo('password', message='Passwords must match')
    ])


class SurveyForm(FlaskForm):
    name = TextField('Name', [Required()])
    description = TextField('Description', [Required()])
    start_date = DateField('Start Date', validators=[Required()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[Required()], format='%Y-%m-%d')
    group_id = SelectField('Group',validators=[Required()])

    def __init__(self):
            super(SurveyForm,self).__init__()
            self.group_id.choices =   [("", "-- Choose a Group --")]+[(str(g.id), g.name) for g in Group.query.order_by(Group.name).all()]
            

class QuestionForm(FlaskForm):
    question_title = TextAreaField('Question', [Required()])
    question_type = SelectField('Question Type', validators=[Required()])
    question_option = TextAreaField('Question Option', [])
    dimension = SelectField('Dimensions', validators=[Required()])

    def __init__(self):
        super(QuestionForm, self).__init__()
        self.question_type.choices =   [("", "-- Choose Question Type --")]+[(str(q.id), q.name) for q in QuestionType.query.order_by(QuestionType.name).all()]
        self.dimension.choices =   [("", "-- Choose a Dimension --")]+[(str(d.id), d.name) for d in Dimensions.query.order_by(Dimensions.name).all()]



class AddQuestionForm(FlaskForm):
    question_title = SelectField('Question', [Required()])
    question_id = HiddenField('', validators=[Required()])

    def __init__(self):
        super(AddQuestionForm, self).__init__()
        self.question_title.choices =   [("", "-- Choose Question --")]+[(str(q.id), q.question_title) for q in Question.query.order_by(Question.question_title).all()]



class AddUserForm(FlaskForm):
    firstname = TextField('First Name', [Required()])
    lastname = TextField('Last Name', [Required()])
    email = TextField('Email', [Required()])
    password = PasswordField('Password', [Required()])
    confirm = PasswordField('Confirm Password', [
        Required(),
        EqualTo('password', message='Passwords must match')
    ])
    user_role = SelectField('User Role', [Required()])
    group_id = SelectField('Group ID', [Required()])
    active_user = SelectField('Active User',[Required()],choices=STATUS)

    def __init__(self):
            super(AddUserForm,self).__init__()
            self.group_id.choices =   [("", "-- Choose a Group --")]+[(str(g.id), g.name) for g in Group.query.order_by(Group.name).all()]
            self.user_role.choices = [("","-- Choose a Role --")]+[(str(r.id), r.name) for r in UserRole.query.order_by(UserRole.name).all()]



class EditUserForm(FlaskForm):
    firstname = TextField('First Name', [Required()])
    lastname = TextField('Last Name', [Required()])
    user_role = SelectField('User Role', [Required()])
    group_id = SelectField('Group ID', [Required()])
    active_user = SelectField('Activate User?',[Required()],choices=STATUS)

    def __init__(self):
            super(EditUserForm,self).__init__()
            self.group_id.choices =   [("", "-- Choose a Group --")]+[(str(g.id), g.name) for g in Group.query.order_by(Group.name).all()]
            self.user_role.choices = [("","-- Choose a Role --")]+[(str(r.id), r.name) for r in UserRole.query.order_by(UserRole.name).all()]











