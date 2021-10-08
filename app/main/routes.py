from datetime import datetime
import urllib.request
from flask import Flask, render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from langdetect import detect, LangDetectException
from app import db
# from app.main.forms import EditProfileForm, EditPostForm, EmptyForm, PostForm, SearchForm
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm
from app.models import User, Post
from app.translate import translate
from app.main import bp
import os


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    form = PostForm()
    if form.validate_on_submit():
        photo = form.photo.data
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'uploads', filename))
            flash('Image successful')
        else:
            flash('Allowed image types are -> png, jpg, jpeg, gif')
        try:
            language = detect(form.description.data)
        except LangDetectException:
            language = ''
        photo_name = filename
        description = form.description.data
        world = form.world.data
        mode = form.mode.data
        materials = form.materials.data
        time_invested = form.time_invested.data
        reddit = form.reddit.data
        link_other = form.link_other.data
        user_id = current_user.id
        post = Post(photo_name, description, world, mode, materials, time_invested, reddit, link_other, user_id, language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your creation is now live!'))
        if request.method == 'POST':
            return redirect(url_for('main.index'))
        else:
            return render_template('_post.html')
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

@bp.route('/uploads/<filename>')
def display_image(filename):
	return redirect(url_for(os.path.join(current_app.config['UPLOAD_FOLDER'], 'uploads', filename)))

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)

# @bp.route('/edit_post', methods=['GET', 'POST'])
# @login_required
# def edit_post():
#     form = EditPostForm(current_post.id)
#     if form.validate_on_submit():
#         current_post.username = form.username.data
#         current_post.about_me = form.about_me.data
#         db.session.commit()
#         flash(_('Your changes have been saved.'))
#         return redirect(url_for('main.edit_profile'))
#     elif request.method == 'GET':
#         form.username.data = current_user.username
#         form.about_me.data = current_user.about_me
#     return render_template('edit_profile.html', title=_('Edit Profile'),
#                            form=form)

@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))

# @bp.route('/like/<post>', methods=['POST'])
# @login_required
# def like(post):
#     form = EmptyForm()
#     if form.validate_on_submit():
#         post = Post.query.filter_by(id=id).first()
#         if post.id is None:
#             flash(_('Post %(id) not found.', id=id))
#             return redirect(url_for('main.index'))
#         if post.user_id == current_user.id:
#             flash(_('You cannot like your own post!'))
#             return redirect(url_for('main.index', id=id))
#         current_user.like(post)
#         db.session.commit()
#         flash(_('You liked this post!', id=id))
#         return redirect(url_for('main.index', id=id))
#     else:
#         return redirect(url_for('main.index'))


# @bp.route('/unlike/<post>', methods=['POST'])
# @login_required
# def unlike(post):
#     form = EmptyForm()
#     if form.validate_on_submit():
#         post = Post.query.filter_by(id=id).first()
#         if post.id is None:
#             flash(_('Post %(id) not found.', id=id))
#             return redirect(url_for('main.index'))
#         if post.user_id == current_user.id:
#             flash(_('You cannot unlike your own post!'))
#             return redirect(url_for('main.index', id=id))
#         current_user.unlike(post)
#         db.session.commit()
#         flash(_('You unliked this post.', id=id))
#         return redirect(url_for('main.index', id=id))
#     else:
#         return redirect(url_for('main.index'))

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)
