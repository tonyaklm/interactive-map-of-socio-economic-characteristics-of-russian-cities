from flask import Flask

from blueprints import user
from flask import render_template
from config import settings

app = Flask(__name__, template_folder="templates")

app.register_blueprint(user.blueprint)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = settings.sqlalchemy_database_uri
app.config['SECRET_KEY'] = settings.secret_key


@app.route('/')
def home():
    return render_template('main.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
