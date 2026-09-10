import re
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, ChangeEmailForm
from ..models import User
from . import auth
from ..email import send_email
from . import db, limiter, oauth


def _generate_username(email):
    base = re.sub(r'[^A-Za-z0-9_.]', '', email.split('@')[0]) or 'user'
    if not base[0].isalpha():
        base = 'user' + base
    username = base
    suffix = 1
    while User.query.filter_by(username=username).first() is not None:
        suffix += 1
        username = '{}{}'.format(base, suffix)
    return username

@auth.route('/login', methods=['GET', 'POSt'])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid username or password')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/google/login')
@limiter.limit("10 per minute")
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth.route('/google/callback')
@limiter.limit("10 per minute")
def google_callback():
    token = oauth.google.authorize_access_token()
    userinfo = token.get('userinfo') or oauth.google.userinfo()
    google_id = userinfo['sub']
    email = userinfo['email']
    email_verified = bool(userinfo.get('email_verified', True))

    user = User.query.filter_by(google_id=google_id).first()
    if user is None:
        user = User.query.filter_by(email=email).first()
        if user is None:
            user = User(email=email,
                        username=_generate_username(email),
                        google_id=google_id,
                        name=userinfo.get('name'),
                        confirmed=email_verified)
            db.session.add(user)
        else:
            user.google_id = google_id
            if email_verified:
                user.confirmed = True
        db.session.commit()

    login_user(user)
    flash('Logged in with Google.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POSt'])
@limiter.limit("5 per hour", methods=["POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash("You have confirmed your account. Thanks!")
    else:
        flash('The confirmation link is invalid or expired.')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():    
    if current_user.is_authenticated:
            current_user.ping()
            if not current_user.confirmed   \
            and request.endpoint    \
            and not request.endpoint.startswith('auth.')    \
            and not request.endpoint.startswith('static'):
                return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
                'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)

@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)

@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))