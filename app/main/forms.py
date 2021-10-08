from flask import request, current_app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, StringField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))

# class EditPostForm(FlaskForm):    
#     photo = FileField(_l('Upload a new photo!'), validators=[FileRequired()])
#     description = TextAreaField(_l('Description'), validators=[DataRequired(), Length(min=0, max=350)])
#     world = StringField(_l('World (overworld, nether or end)'),
#                              validators=[Length(min=0, max=25)])    
#     mode = StringField(_l('Mode (creative, survival or hardcore)'),
#                              validators=[Length(min=0, max=25)])
#     materials = StringField(_l('Materials used (List as many as you like, \
#         especially if the build is in survival or hardcore mode)'),
#                              validators=[Length(min=0, max=350)])
#     time_invested = StringField(_l('Time invested in days, hours and/or minutes'),
#                              validators=[Length(min=0, max=200)])
#     reddit = StringField(_l('Link to r/minecraftbuilds entry, if you have one'),
#                              validators=[Length(min=0, max=300)])
#     link_other = StringField(_l('Link to YouTube, Twitch or other gaming portfolio, if you have them'),
#                              validators=[Length(min=0, max=300)])
#     submit = SubmitField(_l('Submit'))

#     def __init__(self, original_username, *args, **kwargs):
#         super(EditPostForm, self).__init__(*args, **kwargs)
#         self.original_username = original_username

#     def validate_username(self, username):
#         if username.data != self.original_username:
#             user = User.query.filter_by(username=self.username.data).first()
#             if user is not None:
#                 raise ValidationError(_('Please use a different username.'))

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    photo = FileField(_l('Upload a photo!'), validators=[FileRequired()])
    description = TextAreaField(_l('Description'), validators=[DataRequired(), Length(min=0, max=350)])
    world = StringField(_l('World (overworld, nether or end)'),
                             validators=[Length(min=0, max=25)])    
    mode = StringField(_l('Mode (creative, survival or hardcore)'),
                             validators=[Length(min=0, max=25)])
    materials = StringField(_l('Materials used (List as many as you like, \
        especially if the build is in survival or hardcore mode)'),
                             validators=[Length(min=0, max=350)])
    time_invested = StringField(_l('Time invested in days, hours and/or minutes'),
                             validators=[Length(min=0, max=200)])
    reddit = StringField(_l('Link to r/minecraftbuilds entry, if you have one'),
                             validators=[Length(min=0, max=300)])
    link_other = StringField(_l('Link to YouTube, Twitch or other gaming portfolio, if you have them'),
                             validators=[Length(min=0, max=300)])
    submit = SubmitField(_l('Submit'))


class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
