from flask import Flask, redirect, url_for, session, render_template
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from authlib.integrations.flask_client import OAuth
from models import db, User
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

oauth = OAuth(app)
# google = oauth.register(
#     name='google',
#     client_id=Config.GOOGLE_CLIENT_ID,
#     client_secret=Config.GOOGLE_CLIENT_SECRET,
#     access_token_url='https://oauth2.googleapis.com/token',
#     access_token_params=None,
#     authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
#     authorize_params=None,
#     api_base_url='https://www.googleapis.com/oauth2/v3/',
#     client_kwargs={'scope': 'openid email profile'},
# )
google = oauth.register(
    name='google',
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v3/',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/google/secrets')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()

    user = User.query.filter_by(google_id=user_info['sub']).first()
    if not user:
        user = User(
            google_id=user_info['sub'],
            email=user_info['email']
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for('secrets'))

@app.route('/secrets')
@login_required
def secrets():
    return render_template('secrets.html', email=current_user.email)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=3000)
