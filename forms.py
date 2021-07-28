from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    term = StringField('term', validators=[DataRequired()])


class AddSongToQueueForm(FlaskForm):
    link = StringField('link', validators=[DataRequired()])
