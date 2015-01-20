from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required, Length


class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    submit = SubmitField('Submit')


class NewProjectForm(Form):
    name = StringField('Project name', validators=[Required(), Length(0, 64)])
    submit = SubmitField('Submit')


class NewToEmailForm(Form):
    addresses = StringField('Email Addresses', validators=[Required()])
    submit = SubmitField('Submit')
