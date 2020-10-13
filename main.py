#TODO
# Enrégistrer la dernière écoute
# List de bands à écouter

from flask import (Flask,
                   session,
                   redirect,
                   url_for,
                   request,
                   render_template,
                   flash,
                   abort)  # g, escape
from werkzeug.security import (generate_password_hash,
                               check_password_hash)
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms.fields import (StringField,
                            PasswordField,
                            TextAreaField,
                            BooleanField,
                            SubmitField,
                            IntegerField,
                            RadioField,
                            SelectField)
from wtforms.fields.html5 import DateField
from wtforms.widgets import Select
from wtforms.widgets.html5 import (DateInput,
                                   NumberInput)
from wtforms.validators import (DataRequired,
                                Email,
                                EqualTo,
                                Length,
                                Optional,
                                URL)  # Length, NumberRange
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from config import Config
from datetime import datetime
# from cryptography.fernet import Fernet

app = Flask(__name__)
app.config.from_object(Config)
manager = Manager(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)


# Database Model
# ----------------------------------------------------------------------------------------------------------------------
class AppUser(db.Model):
    __tablename__ = 'tapp_user'
    user_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    user_email = db.Column(db.String(80), nullable=False, unique=True)
    user_pass = db.Column(db.String(100), nullable=False)
    activated_ts = db.Column(db.DateTime(), nullable=True)
    audit_crt_ts = db.Column(db.DateTime(), nullable=False)
    audit_upd_ts = db.Column(db.DateTime(), nullable=True)
    user_role = db.Column(db.String(10), nullable=False, default='Régulier')  # Admin or Régulier
    bands = db.relationship('UserBand', backref='tapp_user', lazy='dynamic')  # User's library

    def __init__(self, first_name, last_name, user_email, user_pass, audit_crt_ts):
        self.first_name = first_name
        self.last_name = last_name
        self.user_email = user_email
        self.user_pass = user_pass
        self.audit_crt_ts = audit_crt_ts

    def __repr__(self):
        return '<user: {} {}>'.format(self.first_name, self.last_name)

    def user_name(self):
        return '{} {}'.format(self.first_name, self.last_name)


class Genre(db.Model):
    __tablename__ = 'tgenre'
    genre_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genre_name = db.Column(db.String(50), nullable=False)
    genre_desc = db.Column(db.Text(), nullable=False, default='')
    audit_crt_user_id = db.Column(db.Integer(), nullable=False)
    audit_crt_ts = db.Column(db.DateTime(), nullable=False)
    audit_upd_user_id = db.Column(db.Integer(), nullable=True)
    audit_upd_ts = db.Column(db.DateTime(), nullable=True)
    bands = db.relationship('BandGenre', backref='tgenre', lazy='dynamic')

    def __init__(self, genre_name, genre_desc, audit_crt_user_id, audit_ct_ts):
        self.genre_name = genre_name
        self.genre_desc = genre_desc
        self.audit_crt_user_id = audit_crt_user_id
        self.audit_crt_ts = audit_ct_ts

    def __repr__(self):
        return '<genre: {}>'.format(self.genre_name)


class Band(db.Model):
    __tablename__ = 'tband'
    band_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    band_name = db.Column(db.String(32), nullable=False)
    band_desc = db.Column(db.Text(), nullable=True)
    audit_crt_user_id = db.Column(db.Integer(), nullable=False)
    audit_crt_ts = db.Column(db.DateTime(), nullable=False)
    audit_upd_user_id = db.Column(db.Integer(), nullable=True)
    audit_upd_ts = db.Column(db.DateTime(), nullable=True)
    genres = db.relationship('BandGenre', backref='tband', lazy='dynamic')
    countries = db.relationship('BandCountry', backref='tband', lazy='dynamic')
    comments = db.relationship('BandComment', backref='tband', lazy='dynamic')
    fans = db.relationship('UserBand', backref='tband', lazy='dynamic')  # User's library
    links = db.relationship('BandLink', backref='tband', lazy='dynamic')

    def __init__(self, band_name, band_desc, audit_crt_user_id, audit_ct_ts):
        self.band_name = band_name
        self.band_desc = band_desc
        self.audit_crt_user_id = audit_crt_user_id
        self.audit_crt_ts = audit_ct_ts

    def __repr__(self):
        return '<band: {}:{}>'.format(self.band_id, self.band_name)


class BandLink(db.Model):
    __tablename__ = 'tband_link'
    link_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    band_id = db.Column(db.Integer, db.ForeignKey('tband.band_id'))
    link_name = db.Column(db.String(32), nullable=False)
    link_url = db.Column(db.String(100), nullable=False)
    audit_crt_user_id = db.Column(db.Integer(), nullable=False)
    audit_crt_ts = db.Column(db.DateTime(), nullable=False)
    audit_upd_user_id = db.Column(db.Integer(), nullable=True)
    audit_upd_ts = db.Column(db.DateTime(), nullable=True)

    def __init__(self, band_id, link_name, link_url, audit_crt_user_id, audit_ct_ts):
        self.band_id = band_id
        self.link_name = link_name
        self.link_url = link_url
        self.audit_crt_user_id = audit_crt_user_id
        self.audit_crt_ts = audit_ct_ts

    def __repr__(self):
        return '<link: {}:{}>'.format(self.link_id, self.link_name)


class UserBand(db.Model):
    __tablename__ = 'tuser_band'
    user_band_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('tapp_user.user_id'))
    band_id = db.Column(db.Integer, db.ForeignKey('tband.band_id'))
    audit_crt_ts = db.Column(db.DateTime(), nullable=False)

    def __init__(self, user_id, band_id, audit_crt_ts):
        self.user_id = user_id
        self.band_id = band_id
        self.audit_crt_ts = audit_crt_ts

    def __repr__(self):
        return '<user-band: {}:{}>'.format(self.user_id, self.band_id)


class BandCountry(db.Model):
    __tablename__ = 'tband_country'
    band_country_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    band_id = db.Column(db.Integer, db.ForeignKey('tband.band_id'))
    country_id = db.Column(db.Integer(), db.ForeignKey('tcountry.country_id'))

    def __init__(self, band_id, country_id):
        self.band_id = band_id
        self.country_id = country_id

    def __repr__(self):
        return '<band-country: {}:{}>'.format(self.band_id, self.country_id)


class BandGenre(db.Model):
    __tablename__ = 'tband_genre'
    band_genre_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    band_id = db.Column(db.Integer, db.ForeignKey('tband.band_id'))
    genre_id = db.Column(db.Integer(), db.ForeignKey('tgenre.genre_id'))

    def __init__(self, band_id, genre_id):
        self.band_id = band_id
        self.genre_id = genre_id

    def __repr__(self):
        return '<band-genre: {}:{}>'.format(self.band_id, self.genre_id)


class BandComment(db.Model):
    __tablename__ = 'tband_comment'
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    band_id = db.Column(db.Integer, db.ForeignKey('tband.band_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('tapp_user.user_id'))
    comment_title = db.Column(db.String(80), nullable=False)
    comment_text = db.Column(db.Text(), nullable=True)
    rating = db.Column(db.Integer(), nullable=True)
    audit_crt_user_id = db.Column(db.Integer(), nullable=False)
    audit_crt_ts = db.Column(db.DateTime(), nullable=False)
    audit_upd_user_id = db.Column(db.Integer(), nullable=True)
    audit_upd_ts = db.Column(db.DateTime(), nullable=True)

    def __init__(self, band_id, user_id, comment_title, comment_text, rating, audit_crt_user_id, audit_ct_ts):
        self.band_id = band_id
        self.user_id = user_id
        self.comment_title = comment_title
        self.comment_text = comment_text
        self.rating = rating
        self.audit_crt_user_id = audit_crt_user_id
        self.audit_crt_ts = audit_ct_ts

    def __repr__(self):
        return '<comment: {}:{}>'.format(self.band_id, self.comment_title)


class Country(db.Model):
    __tablename__ = 'tcountry'
    country_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country_code = db.Column(db.Integer, nullable=True)
    country_alpha2 = db.Column(db.String(2), nullable=False)
    country_alpha3 = db.Column(db.String(3), nullable=False)
    country_name_fr = db.Column(db.String(45), nullable=False)
    country_name_en = db.Column(db.String(45), nullable=False)
    bands = db.relationship('BandCountry', backref='tcountry', lazy='dynamic')

    def __init__(self, country_code, country_alpha2, country_alpha3, country_name_fr, country_name_en):
        self.country_code = country_code
        self.country_alpha2 = country_alpha2
        self.country_alpha3 = country_alpha3
        self.country_name_fr = country_name_fr
        self.country_name_en = country_name_en

    def __repr__(self):
        return '<country: {}>'.format(self.country_name_fr)


# Classes pour définir les formulaires WTF
# ----------------------------------------------------------------------------------------------------------------------

# Formulaire pour confirmer la suppression d'une entitée
class DelEntityForm(FlaskForm):
    submit = SubmitField('Supprimer')


# Formulaire web pour l'écran de login
class LoginForm(FlaskForm):
    email = StringField('Courriel', validators=[DataRequired(), Email(message='Le courriel est invalide.')])
    password = PasswordField('Mot de Passe', [DataRequired(message='Le mot de passe est obligatoire.')])
    request_password_change = BooleanField('Changer le mot de passe?')
    password_1 = PasswordField('Nouveau Mot de passe',
                               [EqualTo('password_2', message='Les mots de passe doivent être identiques.')])
    password_2 = PasswordField('Confirmation')
    submit = SubmitField('Se connecter')


# Formulaire web pour l'écran de register
class RegisterForm(FlaskForm):
    first_name = StringField('Prénom', validators=[DataRequired(message='Le prénom est requis.')])
    last_name = StringField('Nom de famille', validators=[DataRequired(message='Le nom de famille est requis.')])
    email = StringField('Courriel', validators=[DataRequired(), Email(message='Le courriel est invalide.')])
    password_1 = PasswordField('Mot de passe',
                               [DataRequired(message='Le mot de passe est obligatoire.'),
                                EqualTo('password_2', message='Les mots de passe doivent être identiques.')])
    password_2 = PasswordField('Confirmation')
    submit = SubmitField('S\'enrégistrer')


# Formulaires pour ajouter un pays
class AddCountryForm(FlaskForm):
    country_code = StringField('Code numérique du pays',
                               validators=[DataRequired(message='Le code est requis.')])
    country_alpha2 = StringField('Code alpha 2',
                                 validators=[DataRequired(message='Le code est requis.'), Length(max=2)])
    country_alpha3 = StringField('Code alpha 3',
                                 validators=[DataRequired(message='Le code est requis.'), Length(max=3)])
    country_name_fr = StringField('Nom français du pays',
                                  validators=[DataRequired(message='Le nom est requis.'), Length(max=45)])
    country_name_en = StringField('Nom anglais du pays',
                                  validators=[DataRequired(message='Le nom est requis.'), Length(max=45)])
    submit = SubmitField('Ajouter')


# Formulaire de la mise à jour d'un pays
class UpdCountryForm(FlaskForm):
    country_code = StringField('Code numérique du pays',
                               validators=[DataRequired(message='Le code est requis.')])
    country_alpha2 = StringField('Code alpha 2',
                                 validators=[DataRequired(message='Le code est requis.'), Length(max=2)])
    country_alpha3 = StringField('Code alpha 3',
                                 validators=[DataRequired(message='Le code est requis.'), Length(max=3)])
    country_name_fr = StringField('Nom français du pays',
                                  validators=[DataRequired(message='Le nom est requis.'), Length(max=45)])
    country_name_en = StringField('Nom anglais du pays',
                                  validators=[DataRequired(message='Le nom est requis.'), Length(max=45)])
    submit = SubmitField('Modifier')


# Formulaires pour ajouter un genre
class AddGenreForm(FlaskForm):
    genre_name = StringField('Nom du genre', validators=[DataRequired(message='Le nom est requis.')])
    genre_desc = TextAreaField('Description')
    submit = SubmitField('Ajouter')


# Formulaire de la mise à jour d'un genre
class UpdGenreForm(FlaskForm):
    genre_name = StringField('Nom du genre', validators=[DataRequired(message='Le nom est requis.')])
    genre_desc = TextAreaField('Description')
    submit = SubmitField('Modifier')


# Formulaires pour ajouter un band
class AddBandForm(FlaskForm):
    band_name = StringField('Nom du band', validators=[DataRequired(message='Le nom est requis.')])
    band_desc = TextAreaField('Description')
    submit = SubmitField('Ajouter')


# Formulaires pour mettre à jour un band
class UpdBandForm(FlaskForm):
    band_name = StringField('Nom du band', validators=[DataRequired(message='Le nom est requis.')])
    band_desc = TextAreaField('Description')
    submit = SubmitField('Modifier')


# Formulaires pour ajouter un band
class AddBandCommentForm(FlaskForm):
    comment_title = StringField('Titre', validators=[DataRequired(message='Le titre est requis.')])
    comment_text = TextAreaField('Commentaire')
    rating = RadioField('Evaluation', choices=[(1, 'Médiocre'), (2, 'Pas très bon'), (3, 'Pas si pire'), (4, 'Bon'),
                                               (5, 'Excellent')])
    submit = SubmitField('Ajouter')


# Formulaires pour mettre à jour un band
class UpdBandCommentForm(FlaskForm):
    comment_title = StringField('Titre', validators=[DataRequired(message='Le titre est requis.')])
    comment_text = TextAreaField('Commentaire')
    rating = RadioField('Evaluation', choices=[(1, 'Médiocre'), (2, 'Pas très bon'), (3, 'Pas si pire'), (4, 'Bon'),
                                               (5, 'Excellent'), (0, "Pas d'évaluation")])
    submit = SubmitField('Modifier')


# Formulaires pour ajouter un link
class AddBandLinkForm(FlaskForm):
    link_name = StringField('Nom du lien', validators=[DataRequired(message='Le nom est requis.')])
    link_url = StringField('URL', validators=[DataRequired(message="Le URL est requis."), URL(message="URL invalide.")])
    submit = SubmitField('Ajouter')


class UpdBandLinkForm(FlaskForm):
    link_name = StringField('Nom du lien', validators=[DataRequired(message='Le nom est requis.')])
    link_url = StringField('URL', validators=[DataRequired(message="Le URL est requis."), URL(message="URL invalide.")])
    submit = SubmitField('Modifier')


# The following functions are views
# ----------------------------------------------------------------------------------------------------------------------
# Custom error pages


@app.errorhandler(404)
def page_not_found(e):
    app.logger.error('Page non trouvée. ' + str(e))
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error('Erreur interne. ' + str(e))
    return render_template('500.html'), 500


# Index
@app.route('/')
def index():
    if not logged_in():
        return redirect(url_for('login'))
    app.logger.debug('Entering index()')
    first_name = session.get('first_name', None)
    return render_template('metal.html', user=first_name)


# Views for Register, logging in, logging out and listing users
@app.route('/login', methods=['GET', 'POST'])
def login():
    # The method is GET when the form is displayed and POST to process the form
    app.logger.debug('Entering login()')
    form = LoginForm()
    if form.validate_on_submit():
        user_email = request.form['email']
        password = request.form['password']
        if db_validate_user(user_email, password):
            session['active_time'] = datetime.now()
            request_pwd_change = request.form.get('request_password_change', None)
            if request_pwd_change:
                app.logger.debug("Changer le mot de passe")
                new_password = request.form['password_1']
                db_change_password(user_email, new_password)
            return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    app.logger.debug('Entering logout()')
    session.pop('user_id', None)
    session.pop('first_name', None)
    session.pop('last_name', None)
    session.pop('user_email', None)
    session.pop('active_time', None)
    flash('Vous êtes maintenant déconnecté.')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    app.logger.debug('Entering register')
    form = RegisterForm()
    if form.validate_on_submit():
        app.logger.debug('Inserting a new registration')
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        user_email = request.form['email']
        user_pass = generate_password_hash(request.form['password_1'])
        if db_user_exists(user_email):
            flash('Cet utilisateur existe déjà. Veuillez vous connecter.')
            return redirect(url_for('login'))
        else:
            if db_add_user(first_name, last_name, user_email, user_pass):
                flash('Vous pourrez vous connecter quand votre utilisateur sera activé.')
                return redirect(url_for('login'))
            else:
                flash('Une erreur de base de données est survenue.')
                abort(500)
    return render_template('register.html', form=form)


@app.route('/list_users')
def list_users():
    if not logged_in():
        return redirect(url_for('login'))
    try:
        user_id = session.get('user_id')
        admin_user = db_user_is_admin(user_id)
        app_users = AppUser.query.order_by(AppUser.first_name).all()
        return render_template('list_users.html', app_users=app_users, admin_user=admin_user)
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return redirect(url_for('index'))


@app.route('/act_user/<int:user_id>', methods=['GET', 'POST'])
def act_user(user_id):
    if not logged_in():
        return redirect(url_for('login'))
    cur_user_id = session.get('user_id')
    if db_user_is_admin(cur_user_id):
        if db_upd_user_status(user_id, 'A'):
            flash("L'utilisateur est activé.")
        else:
            flash("Quelque chose n'a pas fonctionné.")
    else:
        flash("Vous n'êtes pas autorisé à changer le status d'un utilisateur.")
    return redirect(url_for('list_users'))


@app.route('/inact_user/<int:user_id>', methods=['GET', 'POST'])
def inact_user(user_id):
    if not logged_in():
        return redirect(url_for('login'))
    cur_user_id = session.get('user_id')
    if db_user_is_admin(cur_user_id):
        if db_upd_user_status(user_id, 'D'):
            flash("L'utilisateur est désactivé.")
        else:
            flash("Quelque chose n'a pas fonctionné.")
    else:
        flash("Vous n'êtes pas autorisé à changer le status d'un utilisateur.")
    return redirect(url_for('list_users'))


@app.route('/set_user_admin/<int:user_id>', methods=['GET', 'POST'])
def set_user_admin(user_id):
    if not logged_in():
        return redirect(url_for('login'))
    cur_user_id = session.get('user_id')
    if db_user_is_admin(cur_user_id):
        if db_upd_user_role(user_id, 'A'):
            flash("L'utilisateur est maintenant administrateur.")
        else:
            flash("Quelque chose n'a pas fonctionné.")
    else:
        flash("Vous n'êtes pas autorisé à changer le rôle d'un utilisateur.")
    return redirect(url_for('list_users'))


@app.route('/set_user_regular/<int:user_id>', methods=['GET', 'POST'])
def set_user_regular(user_id):
    if not logged_in():
        return redirect(url_for('login'))
    cur_user_id = session.get('user_id')
    if db_user_is_admin(cur_user_id):
        if db_upd_user_role(user_id, 'R'):
            flash("L'utilisateur est maintenant un utilisateur régulier.")
        else:
            flash("Quelque chose n'a pas fonctionné.")
    else:
        flash("Vous n'êtes pas autorisé à changer le rôle d'un utilisateur.")
    return redirect(url_for('list_users'))


@app.route('/del_user/<int:user_id>', methods=['GET', 'POST'])
def del_user(user_id):
    if not logged_in():
        return redirect(url_for('login'))
    cur_user_id = session.get('user_id')
    if db_user_is_admin(cur_user_id):
        form = DelEntityForm()
        if form.validate_on_submit():
            app.logger.debug('Deleting a user')
            # if db_del_user(user_id):
            #    flash("L'utilisateur a été effacé.")
            # else:
            #    flash("Quelque chose n'a pas fonctionné.")
            flash("Il est préférable de désactiver l'utilsateur.")
        else:
            user = db_user_by_id(user_id)
            if user:
                return render_template('del_user.html', form=form, user=user)
            else:
                flash("L'information n'a pas pu être retrouvée.")
    else:
        flash("Vous n'êtes pas autorisé à supprimer un utilisateur.")
    return redirect(url_for('list_users'))


# Views for Lists of Countries
# Ordre des vues: list, show, add, upd, del
@app.route('/list_countries')
def list_countries():
    if not logged_in():
        return redirect(url_for('login'))
    try:
        countries = Country.query.order_by(Country.country_name_fr).all()
        for country in countries:
            country.count_bands = BandCountry.query.filter_by(country_id=country.country_id).count()
        return render_template('list_countries.html', countries=countries)
    except Exception as e:
        flash("Quelque chose n'a pas fonctionné.")
        app.logger.error('Error: ' + str(e))
        abort(500)


@app.route('/show_country/<int:country_id>')
def show_country(country_id):
    if not logged_in():
        return redirect(url_for('login'))
    try:
        country = db_country_by_id(country_id)
        if country:
            return render_template("show_country.html", country=country)
        else:
            flash("L'information n'a pas pu être retrouvée.")
            return redirect(url_for('list_countries'))
    except Exception as e:
        flash("Quelque chose n'a pas fonctionné.")
        app.logger.error('Error: ' + str(e))
        abort(500)


@app.route('/add_country', methods=['GET', 'POST'])
def add_country():
    if not logged_in():
        return redirect(url_for('login'))
    app.logger.debug('Entering add_country')
    form = AddCountryForm()
    if form.validate_on_submit():
        app.logger.debug('Inserting a new country')
        country_code = request.form['country_code']
        country_alpha2 = request.form['country_alpha2']
        country_alpha3 = request.form['country_alpha3']
        country_name_fr = request.form['country_name_fr']
        country_name_en = request.form['country_name_en']
        if db_country_exists_fr(country_name_fr) or db_country_exists_en(country_name_en):
            flash('Ce nom de pays existe déjà.')
            return render_template('add_country.html', form=form)
        else:
            if db_add_country(country_code, country_alpha2, country_alpha3, country_name_fr, country_name_en):
                flash('Le nouveau pays est ajouté.')
                return redirect(url_for('list_countries'))
            else:
                flash('Une erreur de base de données est survenue.')
                abort(500)
    return render_template('add_country.html', form=form)


@app.route('/upd_country/<int:country_id>', methods=['GET', 'POST'])
def upd_country(country_id):
    if not logged_in():
        return redirect(url_for('login'))

    country = db_country_by_id(country_id)
    if country is None:
        flash("L'information n'a pas pu être retrouvée.")
        return redirect(url_for('list_countries'))
    form = UpdCountryForm()
    if form.validate_on_submit():
        app.logger.debug('Updating a country')
        save_country_name_fr = country.country_name_fr
        save_country_name_en = country.country_name_en
        country_name_fr = form.country_name_fr.data
        country_name_en = form.country_name_en.data
        country_code = form.country_code.data
        country_alpha2 = form.country_alpha2.data
        country_alpha3 = form.country_alpha3.data
        if ((country_name_fr != save_country_name_fr) and db_country_exists_fr(country_name_fr)) or \
           ((country_name_en != save_country_name_en) and db_country_exists_en(country_name_en)):
            flash('Ce nom de pays existe déjà')
            return render_template("upd_country.html", form=form, country=country)
        if db_upd_country(country_id, country_code, country_alpha2, country_alpha3, country_name_fr, country_name_en):
            flash("Le pays a été modifié.")
        else:
            flash("Quelque chose n'a pas fonctionné.")
        return redirect(url_for('list_countries'))
    else:
        form.country_code.data = country.country_code
        form.country_alpha2.data = country.country_alpha2
        form.country_alpha3.data = country.country_alpha3
        form.country_name_fr.data = country.country_name_fr
        form.country_name_en.data = country.country_name_en
        return render_template("upd_country.html", form=form, country=country)


@app.route('/del_country/<int:country_id>', methods=['GET', 'POST'])
def del_country(country_id):
    if not logged_in():
        return redirect(url_for('login'))

    form = DelEntityForm()
    if form.validate_on_submit():
        app.logger.debug('Deleting a country')
        if db_del_country(country_id):
            flash("Le pays a été effacé.")
        else:
            flash("Quelque chose n'a pas fonctionné.")
        return redirect(url_for('list_countries'))
    else:
        country = db_country_by_id(country_id)
        if country:
            b_c = BandCountry.query.filter_by(country_id=country_id).first()
            if b_c:
                flash("Ce pays a des bands. Il ne peut pas être effacé.")
            else:
                return render_template('del_country.html', form=form, country=country)
        else:
            flash("L'information n'a pas pu être retrouvée.")
        return redirect(url_for('list_countries'))


# Views for Lists of Genres
# Ordre des vues: list, show, add, upd, del
@app.route('/list_genres')
def list_genres():
    if not logged_in():
        return redirect(url_for('login'))
    try:
        genres = Genre.query.order_by(Genre.genre_name).all()
        for genre in genres:
            genre.count_bands = BandGenre.query.filter_by(genre_id=genre.genre_id).count()
        return render_template('list_genres.html', genres=genres)
    except Exception as e:
        flash("Quelque chose n'a pas fonctionné.")
        app.logger.error('Error: ' + str(e))
        abort(500)


@app.route('/show_genre/<int:genre_id>')
def show_genre(genre_id):
    if not logged_in():
        return redirect(url_for('login'))
    try:
        genre = db_genre_by_id(genre_id)
        if genre:
            u = db_user_by_id(genre.audit_crt_user_id)
            genre.audit_crt_user_name = u.user_name()
            if genre.audit_upd_user_id:
                u = db_user_by_id(genre.audit_upd_user_id)
                genre.audit_upd_user_name = u.user_name()
            return render_template("show_genre.html", genre=genre)
        else:
            flash("L'information n'a pas pu être retrouvée.")
            return redirect(url_for('list_genres'))
    except Exception as e:
        flash("Quelque chose n'a pas fonctionné.")
        app.logger.error('Error: ' + str(e))
        abort(500)


@app.route('/add_genre', methods=['GET', 'POST'])
def add_genre():
    if not logged_in():
        return redirect(url_for('login'))
    app.logger.debug('Entering add_genre')
    form = AddGenreForm()
    if form.validate_on_submit():
        app.logger.debug('Inserting a new genre')
        genre_name = request.form['genre_name']
        genre_desc = request.form['genre_desc']
        if db_genre_exists(genre_name):
            flash('Ce nom de genre existe déjà.')
            return render_template('add_genre.html', form=form)
        else:
            if db_add_genre(genre_name, genre_desc):
                flash('Le nouveau genre est ajouté.')
                return redirect(url_for('list_genres'))
            else:
                flash('Une erreur de base de données est survenue.')
                abort(500)
    return render_template('add_genre.html', form=form)


@app.route('/upd_genre/<int:genre_id>', methods=['GET', 'POST'])
def upd_genre(genre_id):
    if not logged_in():
        return redirect(url_for('login'))
    genre = db_genre_by_id(genre_id)
    if genre is None:
        flash("L'information n'a pas pu être retrouvée.")
        return redirect(url_for('list_genres'))
    form = UpdGenreForm()
    if form.validate_on_submit():
        app.logger.debug('Updating a genre')
        save_genre_name = genre.genre_name
        genre_name = form.genre_name.data
        genre_desc = form.genre_desc.data
        if (genre_name != save_genre_name) and db_genre_exists(genre_name):
            flash('Ce nom de genre existe déjà')
            return render_template("upd_genre.html", form=form, genre=genre)
        if db_upd_genre(genre_id, genre_name, genre_desc):
            flash("Le genre a été modifié.")
        else:
            flash("Quelque chose n'a pas fonctionné.")
        return redirect(url_for('list_genres'))
    else:
        form.genre_name.data = genre.genre_name
        form.genre_desc.data = genre.genre_desc
        return render_template("upd_genre.html", form=form, genre=genre)


@app.route('/del_genre/<int:genre_id>', methods=['GET', 'POST'])
def del_genre(genre_id):
    if not logged_in():
        return redirect(url_for('login'))
    form = DelEntityForm()
    if form.validate_on_submit():
        app.logger.debug('Deleting a genre')
        if db_del_genre(genre_id):
            flash("Le genre a été effacé.")
        else:
            flash("Quelque chose n'a pas fonctionné.")
        return redirect(url_for('list_genres'))
    else:
        genre = db_genre_by_id(genre_id)
        if genre:
            b_g = BandGenre.query.filter_by(genre_id=genre_id).first()
            if b_g:
                flash("Le genre est utilisé. Il ne peut pas être effacé.")
            else:
                return render_template('del_genre.html', form=form, genre=genre)
        else:
            flash("L'information n'a pas pu être retrouvée.")
        return redirect(url_for('list_genres'))


# Views for Lists of Bands
# Ordre des vues: list, show, add, upd, del
@app.route('/list_bands')
def list_bands():
    if not logged_in():
        return redirect(url_for('login'))
    try:
        user_id = session.get('user_id')
        bands = Band.query.order_by(Band.band_name).all()
        for band in bands:
            band.count_fans = UserBand.query.filter_by(band_id=band.band_id).count()
            if db_is_fan(band.band_id, user_id):
                band.is_fan = True
            else:
                band.is_fan = False
            country_list = []
            for b_c in band.countries:
                c = Country.query.get(b_c.country_id)
                country_list.append(c.country_name_fr)
            if len(country_list) > 0:
                band.country_list = ', '.join(country_list)
            else:
                band.country_list = "Pas de pays défini"
            genre_list = []
            for b_g in band.genres:
                g = Genre.query.get(b_g.genre_id)
                genre_list.append(g.genre_name)
            if len(genre_list) > 0:
                band.genre_list = ', '.join(genre_list)
            else:
                band.genre_list = "Pas de genre défini"

        return render_template('list_bands.html', bands=bands)
    except Exception as e:
        flash("Quelque chose n'a pas fonctionné.")
        app.logger.error('Error: ' + str(e))
        abort(500)


@app.route('/show_band/<int:band_id>/<string:return_to>/<int:ent_id>')
def show_band(band_id, return_to, ent_id):
    if not logged_in():
        return redirect(url_for('login'))
    try:
        app.logger.debug("Entering show_band with band_id: " + str(band_id) + " return to: " + return_to +
                         " ent_id: " + str(ent_id))
        band = db_band_by_id(band_id)
        if band:
            u = db_user_by_id(band.audit_crt_user_id)
            band.audit_crt_user_name = u.user_name()
            if band.audit_upd_user_id:
                u = db_user_by_id(band.audit_upd_user_id)
                band.audit_upd_user_name = u.user_name()

            qcomments = BandComment.query.filter_by(band_id=band_id).order_by(BandComment.rating.desc()).all()
            comments = []
            for q_comment in qcomments:
                comment = {'rating': q_comment.rating, 'comment_title': q_comment.comment_title,
                           'comment_text': q_comment.comment_text}
                u = db_user_by_id(q_comment.user_id)
                comment['user_name'] = u.user_name()
                comments.append(comment)

            qcountries = BandCountry.query.filter_by(band_id=band_id).order_by(BandCountry.country_id).all()
            countries = []
            for q_country in qcountries:
                c = db_country_by_id(q_country.country_id)
                countries.append(c.country_name_fr)
            l_countries = ', '.join(countries)

            qgenres = BandGenre.query.filter_by(band_id=band_id).order_by(BandGenre.genre_id).all()
            genres = []
            for q_genre in qgenres:
                g = db_genre_by_id(q_genre.genre_id)
                genres.append(g.genre_name)
            l_genres = ', '.join(genres)

            return render_template("show_band.html", band=band, l_countries=l_countries, l_genres=l_genres,
                                   comments=comments,
                                   return_to=return_to, ent_id=ent_id)
        else:
            flash("L'information n'a pas pu être retrouvée.")
            return redirect(url_for('list_bands'))
    except Exception as e:
        flash("Quelque chose n'a pas fonctionné.")
        app.logger.error('Error: ' + str(e))
        abort(500)


@app.route('/add_band', methods=['GET', 'POST'])
def add_band():
    if not logged_in():
        return redirect(url_for('login'))
    app.logger.debug('Entering add_band')
    form = AddBandForm()
    if form.validate_on_submit():
        app.logger.debug('Inserting a new band')
        band_name = request.form['band_name']
        band_desc = request.form['band_desc']
        if db_add_band(band_name, band_desc):
            flash('Le nouveau band est ajouté.')
            return redirect(url_for('list_bands'))
        else:
            flash('Une erreur de base de données est survenue.')
            abort(500)
    return render_template('add_band.html', form=form)


@app.route('/upd_band/<int:band_id>', methods=['GET', 'POST'])
def upd_band(band_id):
    if not logged_in():
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    band = db_band_by_id(band_id)
    if band is None:
        flash("L'information n'a pas pu être retrouvée.")
        return redirect(url_for('list_bands'))
    session['band_id'] = band_id
    count_countries = 0
    countries = []
    for band_c in band.countries:
        country = {'country_id': band_c.country_id}
        qcountry = Country.query.get(band_c.country_id)
        country['country_name_fr'] = qcountry.country_name_fr
        country['country_name_en'] = qcountry.country_name_en
        countries.append(country)
        count_countries += 1
    count_genres = 0
    genres = []
    for band_g in band.genres:
        genre = {'genre_id': band_g.genre_id}
        qgenre = Genre.query.get(band_g.genre_id)
        genre['genre_name'] = qgenre.genre_name
        genres.append(genre)
        count_genres += 1
    count_links = 0
    links = []
    for link in band.links:
        count_links += 1

    band_comment = BandComment.query.filter_by(band_id=band_id, user_id=user_id).first()

    form = UpdBandForm()
    if form.validate_on_submit():
        app.logger.debug('Updating a band')
        # save_band_name = band.band_name
        band_name = form.band_name.data
        band_desc = form.band_desc.data
        # if (band_name != save_band_name) and db_band_exists(band_name):
        #     flash('Ce nom de band existe déjà')
        #     return render_template("upd_band.html", form=form, band=band)
        if db_upd_band(band_id, band_name, band_desc):
            flash("Le band a été modifié.")
        else:
            flash("Quelque chose n'a pas fonctionné.")
        return redirect(url_for('list_bands'))
    else:
        form.band_name.data = band.band_name
        form.band_desc.data = band.band_desc
        return render_template("upd_band.html", form=form, band=band,
                               countries=countries, count_countries=count_countries,
                               genres=genres, count_genres=count_genres,
                               band_comment=band_comment, count_links=count_links)


@app.route('/del_band/<int:band_id>', methods=['GET', 'POST'])
def del_band(band_id):
    if not logged_in():
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    form = DelEntityForm()
    if form.validate_on_submit():
        app.logger.debug('Deleting a band')
        if db_del_band(band_id):
            flash("Le band a été effacé.")
        else:
            flash("Quelque chose n'a pas fonctionné.")
        return redirect(url_for('list_bands'))
    else:
        band = db_band_by_id(band_id)
        if band:
            fan = UserBand.query.filter(UserBand.band_id == band_id, UserBand.user_id != user_id).first()
            if fan:
                flash("Le band a un autre fan que toi, donc tu ne peux pas l'effacer.")
            else:
                return render_template('del_band.html', form=form, band=band)
        else:
            flash("L'information n'a pas pu être retrouvée.")
        return redirect(url_for('list_bands'))


@app.route('/list_my_bands')
def list_my_bands():
    if not logged_in():
        return redirect(url_for('login'))
    try:
        user_id = session.get('user_id')
        results = UserBand.query.join(Band) \
            .filter(UserBand.user_id == user_id) \
            .add_columns(Band.band_id, Band.band_name) \
            .order_by(Band.band_name)

        bands = []
        for row in results:
            band = dict()
            band['band_id'] = row[1]
            band['band_name'] = row[2]
            bands.append(band)

        for band in bands:
            band['count_fans'] = UserBand.query.filter_by(band_id=band['band_id']).count()

            countries = BandCountry.query.join(Country, BandCountry.country_id == Country.country_id) \
                .filter(BandCountry.band_id == band['band_id']) \
                .add_columns(Country.country_name_fr).order_by(Country.country_name_fr)
            country_list = []
            for row in countries:
                country_list.append(row[1])
            if len(country_list) > 0:
                band['country_list'] = ', '.join(country_list)
            else:
                band['country_list'] = "Pas de pays défini"

            genres = BandGenre.query.join(Genre, BandGenre.genre_id == Genre.genre_id) \
                .filter(BandGenre.band_id == band['band_id']) \
                .add_columns(Genre.genre_name).order_by(Genre.genre_name)
            genre_list = []
            for row in genres:
                genre_list.append(row[1])
            if len(genre_list) > 0:
                band['genre_list'] = ', '.join(genre_list)
            else:
                band['genre_list'] = "Pas de genre défini"
        return render_template('list_my_bands.html', bands=bands)
    except Exception as e:
        flash("Quelque chose n'a pas fonctionné.")
        app.logger.error('Error: ' + str(e))
        abort(500)


@app.route('/list_bands_by_country/<int:country_id>')
def list_bands_by_country(country_id):
    if not logged_in():
        return redirect(url_for('login'))
    try:
        user_id = session.get('user_id')
        country = db_country_by_id(country_id)
        results = BandCountry.query.join(Band) \
            .filter(BandCountry.country_id == country_id) \
            .add_columns(Band.band_id, Band.band_name) \
            .order_by(Band.band_name)
        bands = []
        for row in results:
            band = dict()
            band['band_id'] = row[1]
            band['band_name'] = row[2]
            bands.append(band)

        for band in bands:
            band['count_fans'] = UserBand.query.filter_by(band_id=band['band_id']).count()
            if db_is_fan(band['band_id'], user_id):
                band['is_fan'] = True
            else:
                band['is_fan'] = False

            countries = BandCountry.query.join(Country, BandCountry.country_id == Country.country_id) \
                .filter(BandCountry.band_id == band['band_id']) \
                .add_columns(Country.country_name_fr).order_by(Country.country_name_fr)
            country_list = []
            for row in countries:
                country_list.append(row[1])
            if len(country_list) > 0:
                band['country_list'] = ', '.join(country_list)
            else:
                band['country_list'] = "Pas de pays défini"

            genres = BandGenre.query.join(Genre, BandGenre.genre_id == Genre.genre_id) \
                .filter(BandGenre.band_id == band['band_id']) \
                .add_columns(Genre.genre_name).order_by(Genre.genre_name)
            genre_list = []
            for row in genres:
                genre_list.append(row[1])
            if len(genre_list) > 0:
                band['genre_list'] = ', '.join(genre_list)
            else:
                band['genre_list'] = "Pas de genre défini"
        return render_template('list_bands_by_country.html', country=country, bands=bands)
    except Exception as e:
        flash("Quelque chose n'a pas fonctionné.")
        app.logger.error('Error: ' + str(e))
        abort(500)


@app.route('/list_bands_by_genre/<int:genre_id>')
def list_bands_by_genre(genre_id):
    if not logged_in():
        return redirect(url_for('login'))
    try:
        user_id = session.get('user_id')
        genre = db_genre_by_id(genre_id)
        results = BandGenre.query.join(Band, BandGenre.band_id == Band.band_id) \
            .filter(BandGenre.genre_id == genre_id) \
            .add_columns(Band.band_id, Band.band_name) \
            .order_by(Band.band_name)

        bands = []
        for row in results:
            app.logger.debug(type(row))
            band = dict()
            app.logger.debug(type(band))
            app.logger.debug('Band ID: ' + str(row[1]))
            app.logger.debug('Band name: ' + row[2])
            band['band_id'] = row[1]
            band['band_name'] = row[2]
            bands.append(band)

        for band in bands:
            band['count_fans'] = UserBand.query.filter_by(band_id=band['band_id']).count()
            if db_is_fan(band['band_id'], user_id):
                band['is_fan'] = True
            else:
                band['is_fan'] = False

            countries = BandCountry.query.join(Country, BandCountry.country_id == Country.country_id) \
                .filter(BandCountry.band_id == band['band_id']) \
                .add_columns(Country.country_name_fr).order_by(Country.country_name_fr)
            country_list = []
            for row in countries:
                country_list.append(row[1])
            if len(country_list) > 0:
                band['country_list'] = ', '.join(country_list)
            else:
                band['country_list'] = "Pas de pays défini"

            genres = BandGenre.query.join(Genre, BandGenre.genre_id == Genre.genre_id) \
                .filter(BandGenre.band_id == band['band_id']) \
                .add_columns(Genre.genre_name).order_by(Genre.genre_name)
            genre_list = []
            for row in genres:
                genre_list.append(row[1])
            if len(genre_list) > 0:
                band['genre_list'] = ', '.join(genre_list)
            else:
                band['genre_list'] = "Pas de genre défini"

        return render_template('list_bands_by_genre.html', genre=genre, bands=bands)
    except Exception as e:
        flash("Quelque chose n'a pas fonctionné.")
        app.logger.error('Error: ' + str(e))
        abort(500)


@app.route('/add_fan/<int:band_id>')
def add_fan(band_id):
    if not logged_in():
        return redirect(url_for('login'))
    app.logger.debug('Entering add_fan')
    user_id = session.get('user_id')
    if db_add_fan(band_id, user_id):
        flash('Le band a été ajouté à ta liste.')
        return redirect(url_for('list_bands'))
    else:
        flash('Une erreur de base de données est survenue.')
        abort(500)


@app.route('/del_fan/<int:band_id>')
def del_fan(band_id):
    if not logged_in():
        return redirect(url_for('login'))
    app.logger.debug('Entering add_fan')
    user_id = session.get('user_id')
    if db_del_fan(band_id, user_id):
        flash('Le band a été enlevé de ta liste.')
        return redirect(url_for('list_bands'))
    else:
        flash('Une erreur de base de données est survenue.')
        abort(500)


# Views for BandCountry
# Ordre des vues: sel, add, del
@app.route('/sel_band_country/<int:band_id>')
def sel_band_country(band_id):
    if not logged_in():
        return redirect(url_for('login'))

    band_countries = BandCountry.query.filter_by(band_id=band_id).all()
    for b_c in band_countries:
        country = Country.query.filter_by(country_id=b_c.country_id).first()
        b_c.country_name_fr = country.country_name_fr
        b_c.country_name_en = country.country_name_en

    tmp_countries = Country.query.order_by(Country.country_name_fr).all()
    countries = []
    for c in tmp_countries:
        if not db_band_country_exists(band_id, c.country_id):
            countries.append(c)
    return render_template('sel_band_country.html', band_id=band_id, countries=countries, band_countries=band_countries)


@app.route('/add_band_country/<int:band_id>/<int:country_id>')
def add_band_country(band_id, country_id):
    if not logged_in():
        return redirect(url_for('login'))
    app.logger.debug('Entering add_band_country')
    if db_add_band_country(band_id, country_id):
        flash("Le pays a été ajouté au band.")
        return redirect(url_for('upd_band', band_id=band_id))
    else:
        flash('Une erreur de base de données est survenue.')
        abort(500)


@app.route('/del_band_country/<int:country_id>')
def del_band_country(country_id):
    if not logged_in():
        return redirect(url_for('login'))
    app.logger.debug('Entering del_band_country')
    band_id = session.get('band_id')
    if db_del_band_country(band_id, country_id):
        flash("Le pays a été enlevé.")
        return redirect(url_for('upd_band', band_id=band_id))
    else:
        flash('Une erreur de base de données est survenue.')
        abort(500)


# Views for Bandgenre
# Ordre des vues: sel, add, del
@app.route('/sel_band_genre/<int:band_id>')
def sel_band_genre(band_id):
    if not logged_in():
        return redirect(url_for('login'))

    band_genres = BandGenre.query.filter_by(band_id=band_id).all()
    for b_g in band_genres:
        genre = Genre.query.filter_by(genre_id=b_g.genre_id).first()
        b_g.genre_name = genre.genre_name

    tmp_genres = Genre.query.order_by(Genre.genre_name).all()
    genres = []
    for g in tmp_genres:
        if not db_band_genre_exists(band_id, g.genre_id):
            genres.append(g)
    return render_template('sel_band_genre.html', band_id=band_id, genres=genres, band_genres=band_genres)


@app.route('/add_band_genre/<int:genre_id>')
def add_band_genre(genre_id):
    if not logged_in():
        return redirect(url_for('login'))
    app.logger.debug('Entering add_band_genre')
    band_id = session.get('band_id')
    if db_add_band_genre(band_id, genre_id):
        flash("Le genre a été ajouté au band.")
        return redirect(url_for('sel_band_genre', band_id=band_id))
    else:
        flash('Une erreur de base de données est survenue.')
        abort(500)


@app.route('/del_band_genre/<int:genre_id>')
def del_band_genre(genre_id):
    if not logged_in():
        return redirect(url_for('login'))
    app.logger.debug('Entering del_band_genre')
    band_id = session.get('band_id')
    if db_del_band_genre(band_id, genre_id):
        flash("Le genre a été enlevé pour ce band.")
        return redirect(url_for('sel_band_genre', band_id=band_id))
    else:
        flash('Une erreur de base de données est survenue.')
        abort(500)


@app.route('/add_band_comment', methods=['GET', 'POST'])
def add_band_comment():
    if not logged_in():
        return redirect(url_for('login'))
    app.logger.debug('Entering add_band_comment')
    band_id = session.get('band_id')
    user_id = session.get('user_id')
    form = AddBandCommentForm()
    if form.validate_on_submit():
        app.logger.debug('Inserting a new band comment')
        comment_title = request.form['comment_title']
        comment_text = request.form['comment_text']
        rating = request.form['rating']
        if db_add_band_comment(band_id, user_id, comment_title, comment_text, rating):
            flash('Le nouveau commentaire est ajouté.')
            return redirect(url_for('upd_band', band_id=band_id))
        else:
            flash('Une erreur de base de données est survenue.')
            abort(500)
    form.rating.data = 0
    return render_template('add_band_comment.html', form=form, band_id=band_id)


@app.route('/upd_band_comment/<int:comment_id>', methods=['GET', 'POST'])
def upd_band_comment(comment_id):
    if not logged_in():
        return redirect(url_for('login'))
    band_id = session.get('band_id')
    comment = db_band_comment_by_id(comment_id)
    if comment is None:
        flash("L'information n'a pas pu être retrouvée.")
        return redirect(url_for('upd_band', band_id=band_id))
    form = UpdBandCommentForm()
    if form.validate_on_submit():
        app.logger.debug('Updating a genre')
        rating = form.rating.data
        comment_title = form.comment_title.data
        comment_text = form.comment_text.data
        if db_upd_band_comment(comment_id, comment_title, comment_text, rating):
            flash("Le commentaire a été modifié.")
        else:
            flash("Quelque chose n'a pas fonctionné.")
        return redirect(url_for('upd_band', band_id=band_id))
    else:
        form.rating.default = comment.rating
        form.process()
        form.comment_title.data = comment.comment_title
        form.comment_text.data = comment.comment_text
        return render_template("upd_band_comment.html", form=form, comment=comment)


@app.route('/del_band_comment/<int:comment_id>', methods=['GET', 'POST'])
def del_band_comment(comment_id):
    if not logged_in():
        return redirect(url_for('login'))
    band_id = session.get('band_id')
    form = DelEntityForm()
    if form.validate_on_submit():
        app.logger.debug('Deleting a comment')
        if db_del_band_comment(comment_id):
            flash("Le commentaire a été effacé.")
        else:
            flash("Quelque chose n'a pas fonctionné.")
        return redirect(url_for('upd_band', band_id=band_id))
    else:
        comment = db_band_comment_by_id(comment_id)
        if comment:
            return render_template('del_band_comment.html', form=form, comment=comment)
        else:
            flash("L'information n'a pas pu être retrouvée.")
            return redirect(url_for('upd_band', band_id=band_id))


@app.route('/add_band_link', methods=['GET', 'POST'])
def add_band_link():
    if not logged_in():
        return redirect(url_for('login'))
    app.logger.debug('Entering add_band_link')
    band_id = session.get('band_id')
    form = AddBandLinkForm()
    if form.validate_on_submit():
        app.logger.debug('Inserting a new link')
        link_name = request.form['link_name']
        link_url = request.form['link_url']
        if db_add_band_link(band_id, link_name, link_url):
            flash('Le nouveau lien est ajouté.')
            return redirect(url_for('upd_band', band_id=band_id))
        else:
            flash('Une erreur de base de données est survenue.')
            abort(500)
    return render_template('add_band_link.html', form=form, band_id=band_id)


@app.route('/upd_band_link/<int:link_id>', methods=['GET', 'POST'])
def upd_band_link(link_id):
    if not logged_in():
        return redirect(url_for('login'))
    band_id = session.get('band_id')
    link = db_band_link_by_id(link_id)
    if link is None:
        flash("L'information n'a pas pu être retrouvée.")
        return redirect(url_for('upd_band', band_id=band_id))
    form = UpdBandLinkForm()
    if form.validate_on_submit():
        app.logger.debug('Updating a link')
        link_name = form.link_name.data
        link_url = form.link_url.data
        if db_upd_band_link(link_id, link_name, link_url):
            flash("Le lien a été modifié.")
        else:
            flash("Quelque chose n'a pas fonctionné.")
        return redirect(url_for('upd_band', band_id=band_id))
    else:
        form.link_name.data = link.link_name
        form.link_url.data = link.link_url
        return render_template("upd_band_link.html", form=form, link=link)


@app.route('/del_band_link/<int:link_id>', methods=['GET', 'POST'])
def del_band_link(link_id):
    if not logged_in():
        return redirect(url_for('login'))
    band_id = session.get('band_id')
    form = DelEntityForm()
    if form.validate_on_submit():
        app.logger.debug('Deleting a link')
        if db_del_band_link(link_id):
            flash("Le lien a été effacé.")
        else:
            flash("Quelque chose n'a pas fonctionné.")
        return redirect(url_for('upd_band', band_id=band_id))
    else:
        link = db_band_link_by_id(link_id)
        if link:
            return render_template('del_band_link.html', form=form, link=link)
        else:
            flash("L'information n'a pas pu être retrouvée.")
            return redirect(url_for('upd_band', band_id=band_id))


# Application functions
# ----------------------------------------------------------------------------------------------------------------------
def logged_in():
    user_email = session.get('user_email', None)
    if user_email:
        active_time = session['active_time']
        delta = datetime.now() - active_time
        if (delta.days > 0) or (delta.seconds > 1800):
            flash('Votre session est expirée.')
            return False
        session['active_time'] = datetime.now()
        return True
    else:
        return False


# Database functions
# ----------------------------------------------------------------------------------------------------------------------

# Database functions for AppUser
def db_add_user(first_name, last_name, user_email, user_pass):
    audit_crt_ts = datetime.now()
    try:
        user = AppUser(first_name, last_name, user_email, user_pass, audit_crt_ts)
        if user_email == app.config.get('ADMIN_EMAILID'):
            user.activated_ts = datetime.now()
            user.user_role = 'SuperAdmin'
        else:
            user.user_role = 'Régulier'
        db.session.add(user)
        db.session.commit()
        return True
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False


def db_upd_user_status(user_id, status):
    try:
        user = AppUser.query.get(user_id)
        if status == 'A':
            user.activated_ts = datetime.now()
        else:
            user.activated_ts = None
        db.session.commit()
        return True
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False


def db_upd_user_role(user_id, user_role):
    try:
        user = AppUser.query.get(user_id)
        if user_role == 'A':
            user.user_role = 'Admin'
        else:
            user.user_role = 'Régulier'
        db.session.commit()
        return True
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False


def db_user_exists(user_email):
    app.logger.debug('Entering user_exists with: ' + user_email)
    try:
        user = AppUser.query.filter_by(user_email=user_email).first()
        if user is None:
            return False
        else:
            return True
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False


def db_user_is_admin(user_id):
    app.logger.debug('Entering db_user_is_admin with: ' + str(user_id))
    try:
        user = AppUser.query.get(user_id)
        if user is None:
            return False
        else:
            if user.user_role in ['Admin', 'SuperAdmin']:
                return True
            else:
                return False
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False


def db_user_by_id(user_id):
    try:
        u = AppUser.query.get(user_id)
        return u
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return None


def db_change_password(user_email, new_password):
    try:
        user = AppUser.query.filter_by(user_email=user_email).first()
        if user is None:
            flash("Mot de passe inchangé. L'utilisateur n'a pas été retrouvé.")
            return False
        else:
            user.user_pass = generate_password_hash(new_password)
            user.audit_upd_ts = datetime.now()
            db.session.commit()
            flash("Mot de passe changé.")
            return True
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        flash("Mot de passe inchangé. Une erreur interne s'est produite.")
        return False


# Validate if a user is defined in tapp_user with the proper password.
def db_validate_user(user_email, password):
    try:
        user = AppUser.query.filter_by(user_email=user_email).first()
        if user is None:
            flash("L'utilisateur n'existe pas.")
            return False

        if not user.activated_ts:
            flash("L'utilisateur n'est pas activé.")
            return False

        if check_password_hash(user.user_pass, password):
            session['user_id'] = user.user_id
            session['user_email'] = user.user_email
            session['first_name'] = user.first_name
            session['last_name'] = user.last_name
            return True
        else:
            flash("Mauvais mot de passe!")
            return False
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        flash("Connection impossible. Une erreur interne s'est produite.")
        return False


def db_del_user(user_id):
    try:
        user = AppUser.query.get(user_id)
        for note in user.notes:
            db.session.delete(note)
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


# DB functions for Country: exists, by_id, add, upd, del, others
def db_country_exists_fr(country_name):
    app.logger.debug('Entering country_exists with: ' + country_name)
    try:
        country = Country.query.filter_by(country_name_fr=country_name).first()
        if country is None:
            return False
        else:
            return True
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False


def db_country_exists_en(country_name):
    app.logger.debug('Entering country_exists with: ' + country_name)
    try:
        country = Country.query.filter_by(country_name_en=country_name).first()
        if country is None:
            return False
        else:
            return True
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False


def db_country_by_id(country_id):
    try:
        country = Country.query.get(country_id)
        if country:
            return country
        else:
            return None
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return None


def db_add_country(country_code, country_alpha2, country_alpha3, country_name_fr, country_name_en):
    country = Country(country_code, country_alpha2, country_alpha3, country_name_fr, country_name_en)
    try:
        db.session.add(country)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_upd_country(country_id, country_code, country_alpha2, country_alpha3, country_name_fr, country_name_en):
    try:
        country = Country.query.get(country_id)
        country.country_code = country_code
        country.country_alpha2 = country_alpha2
        country.country_alpha3 = country_alpha3
        country.country_name_fr = country_name_fr
        country.country_name_en = country_name_en
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_del_country(country_id):
    try:
        country = Country.query.get(country_id)
        db.session.delete(country)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


# DB functions for Genre: exists, by_id, add, upd, del, others
def db_genre_exists(genre_name):
    app.logger.debug('Entering genre_exists with: ' + genre_name)
    try:
        genre = Genre.query.filter_by(genre_name=genre_name).first()
        if genre is None:
            return False
        else:
            return True
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False


def db_genre_by_id(genre_id):
    try:
        genre = Genre.query.get(genre_id)
        if genre:
            return genre
        else:
            return None
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return None


def db_add_genre(genre_name, genre_desc):
    audit_crt_user_id = session.get('user_id', None)
    audit_crt_ts = datetime.now()
    genre = Genre(genre_name, genre_desc, audit_crt_user_id, audit_crt_ts)
    try:
        db.session.add(genre)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_upd_genre(genre_id, genre_name, genre_desc):
    audit_upd_user = session.get('user_id', None)
    audit_upd_ts = datetime.now()
    try:
        genre = Genre.query.get(genre_id)
        genre.genre_name = genre_name
        genre.genre_desc = genre_desc
        genre.audit_upd_user = audit_upd_user
        genre.audit_upd_ts = audit_upd_ts
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_del_genre(genre_id):
    try:
        genre = Genre.query.get(genre_id)
        db.session.delete(genre)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


# DB functions for Band: exists, by_id, add, upd, del, others
def db_band_exists(band_name):   # Peut-être une fonction inutile. On permet les doublon de band_name.
    app.logger.debug('Entering band_exists with: ' + band_name)
    try:
        band = Band.query.filter_by(band_name=band_name).first()
        if band is None:
            return False
        else:
            return True
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False


def db_band_by_id(band_id):
    try:
        band = Band.query.get(band_id)
        if band:
            return band
        else:
            return None
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return None


def db_add_band(band_name, band_desc):
    audit_crt_user_id = session.get('user_id', None)
    audit_crt_ts = datetime.now()
    band = Band(band_name, band_desc, audit_crt_user_id, audit_crt_ts)
    try:
        db.session.add(band)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_upd_band(band_id, band_name, band_desc):
    audit_upd_user = session.get('user_id', None)
    audit_upd_ts = datetime.now()
    try:
        band = Band.query.get(band_id)
        band.band_name = band_name
        band.band_desc = band_desc
        band.audit_upd_user = audit_upd_user
        band.audit_upd_ts = audit_upd_ts
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_del_band(band_id):
    try:
        band = Band.query.get(band_id)
        for fan in band.fans:
            db.session.delete(fan)
        for genre in band.genres:
            db.session.delete(genre)
        for country in band.countries:
            db.session.delete(country)
        for link in band.links:
            db.session.delete(link)
        db.session.delete(band)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_is_fan(band_id, user_id):
    app.logger.debug('Entering db_is_fan with: ' + str(band_id) + ':' + str(user_id))
    try:
        fan = UserBand.query.filter_by(band_id=band_id, user_id=user_id).first()
        if fan is None:
            return False
        else:
            return True
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False


def db_add_fan(band_id, user_id):
    audit_crt_ts = datetime.now()
    fan = UserBand(user_id, band_id, audit_crt_ts)
    try:
        db.session.add(fan)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_del_fan(band_id, user_id):
    try:
        fan = UserBand.query.filter_by(band_id=band_id, user_id=user_id).first()
        db.session.delete(fan)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_band_country_exists(band_id, country_id):
    app.logger.debug('Entering band_country_exists with: ' + str(band_id) + ':' + str(country_id))
    try:
        b_c = BandCountry.query.filter_by(band_id=band_id, country_id=country_id).first()
        if b_c is None:
            return False
        else:
            return True
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False


def db_add_band_country(band_id, country_id):
    b_c = BandCountry(band_id, country_id)
    try:
        db.session.add(b_c)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_del_band_country(band_id, country_id):
    try:
        b_c = BandCountry.query.filter_by(band_id=band_id, country_id=country_id).first()
        db.session.delete(b_c)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_band_genre_exists(band_id, genre_id):
    app.logger.debug('Entering band_genre_exists with: ' + str(band_id) + ':' + str(genre_id))
    try:
        b_g = BandGenre.query.filter_by(band_id=band_id, genre_id=genre_id).first()
        if b_g is None:
            return False
        else:
            return True
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False


def db_add_band_genre(band_id, genre_id):
    b_g = BandGenre(band_id, genre_id)
    try:
        db.session.add(b_g)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_del_band_genre(band_id, genre_id):
    try:
        b_g = BandGenre.query.filter_by(band_id=band_id, genre_id=genre_id).first()
        db.session.delete(b_g)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_band_comment_by_id(comment_id):
    try:
        comment = BandComment.query.get(comment_id)
        if comment:
            return comment
        else:
            return None
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return None


def db_add_band_comment(band_id, user_id, comment_title, comment_text, rating):
    audit_crt_user = session.get('user_id', None)
    audit_crt_ts = datetime.now()
    cmt = BandComment(band_id, user_id, comment_title, comment_text, rating, audit_crt_user, audit_crt_ts)
    try:
        db.session.add(cmt)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_upd_band_comment(comment_id, comment_title, comment_text, rating):
    audit_upd_user = session.get('user_id', None)
    audit_upd_ts = datetime.now()
    try:
        comment = BandComment.query.get(comment_id)
        comment.comment_title = comment_title
        comment.comment_text = comment_text
        comment.rating = rating
        comment.audit_upd_user = audit_upd_user
        comment.audit_upd_ts = audit_upd_ts
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_del_band_comment(comment_id):
    try:
        comment = BandComment.query.get(comment_id)
        db.session.delete(comment)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_band_link_by_id(link_id):
    try:
        link = BandLink.query.get(link_id)
        if link:
            return link
        else:
            return None
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return None


def db_add_band_link(band_id, link_name, link_url):
    audit_crt_user = session.get('user_id', None)
    audit_crt_ts = datetime.now()
    link = BandLink(band_id, link_name, link_url, audit_crt_user, audit_crt_ts)
    try:
        db.session.add(link)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_upd_band_link(link_id, link_name, link_url):
    audit_upd_user = session.get('user_id', None)
    audit_upd_ts = datetime.now()
    try:
        link = BandLink.query.get(link_id)
        link.link_name = link_name
        link.link_url = link_url
        link.audit_upd_user = audit_upd_user
        link.audit_upd_ts = audit_upd_ts
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


def db_del_band_link(link_id):
    try:
        link = BandLink.query.get(link_id)
        db.session.delete(link)
        db.session.commit()
    except Exception as e:
        app.logger.error('Error: ' + str(e))
        return False
    return True


# Start the server for the application
if __name__ == '__main__':
    manager.run()
