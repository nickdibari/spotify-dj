from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class AddSongToQueueForm(FlaskForm):
    link = StringField('link', validators=[DataRequired()])
