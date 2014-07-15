from wtforms.form import Form
from wtforms.fields import StringField, TextAreaField
from wtforms.validators import InputRequired


class PostForm(Form):
    title = StringField(u'Title', [InputRequired("Title is required")])
    body = TextAreaField(u'Post body', [InputRequired("Body is required")])
