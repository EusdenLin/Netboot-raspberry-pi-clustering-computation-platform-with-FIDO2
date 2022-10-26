import SQLAlchemy
from flask import Flask

db = SQLAlchemy()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

db.init(app)

@app.route('/create_db')
def index():
	db.create_all()
	return 'OK'

if __name__ == "__main__":
	app.run()
