from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class AddSongToQueueForm(FlaskForm):
    uri = StringField('uri', validators=[DataRequired()])
