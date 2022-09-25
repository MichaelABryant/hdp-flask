from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Email, Regexp, Optional
from ..models import Role, User
from wtforms import ValidationError
    
class HeartInformationForm(FlaskForm):
    patient_name = StringField('Patient name:', validators=[DataRequired()])
    age = IntegerField('Age:', validators=[DataRequired(),
                                           NumberRange(min=0, max=None)])
    sex = SelectField('Sex:', choices=[('', ''),
                                       ('0', 'Female'),
                                       ('1', 'Male')])
    cp = SelectField('Chest pain type:', choices=[('', ''),
                                                  ('1', 'Typical'),
                                                  ('2', 'Atypical'),
                                                  ('3', 'Non-anginal'),
                                                  ('4', 'Asymptomatic')])
    trestbps = FloatField('Resting blood pressure (mmHg):',
                          validators=[DataRequired(),
                                      NumberRange(min=0,max=None)])
    chol = FloatField('Cholesterol (mg/dL):',
                      validators=[DataRequired(),NumberRange(min=0,max=None)])
    fbs = SelectField('Fasting blood sugar greater than 120 mg/dL:',
                      choices=[('', ''), ('0', 'False'), ('1', 'True')])
    restecg = SelectField('ECG:', choices=[('', ''),
                                           ('0', 'Normal'),
                                           ('1', 'Abnormal'),
                                           ('2', 'Hypertrophy')])
    thalach = FloatField('Maximum heart rate (bpm):',
                         validators=[DataRequired(),
                                     NumberRange(min=0,max=None)])
    exang = SelectField('Exercise-induced angina:',
                        choices=[('', ''), ('0', 'False'), ('1', 'True')])
    oldpeak = FloatField('ST-depression:',
                         validators=[DataRequired(),
                                     NumberRange(min=0,max=None)])
    slope = SelectField('ST segment slope characteristic:',
                        choices=[('', ''),
                                 ('1', 'Upsloping'),
                                 ('2', 'Flat'), ('3', 'Downsloping')])
    ca = IntegerField('Number of major vessels colored by fluoroscopy:',
                      validators=[DataRequired(), NumberRange(min=0, max=3)])
    thal = SelectField('Thalium stress test:',
                       choices=[('', ''),
                                ('0', 'Did not take test'),
                                ('3', 'Normal'), ('6', 'Fixed defect'),
                                ('7', 'Reversible defect')])
    submit = SubmitField('Predict')

class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[Length(0,64)])
    location = StringField('Location', validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')    
    
class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
            
class SearchBarForm(FlaskForm):
    name = StringField('Name', validators=[Length(0,64), Optional()])
    search = SubmitField('Search')