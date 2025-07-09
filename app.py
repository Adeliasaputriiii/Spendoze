from flask import Flask, render_template, request, redirect, url_for
from routes.home_route import home_bp
from routes.account_route import login_bp
from routes.upload_route import upload_bp
from routes.result_route import result_bp
from routes.save_route import save_bp
from db import get_db_connection

from dotenv import load_dotenv 
import os                       
load_dotenv()                   

app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv("SECRET_KEY")

# Register Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(login_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(result_bp)
app.register_blueprint(save_bp)

if __name__ == '__main__':
    app.run(debug=True)
