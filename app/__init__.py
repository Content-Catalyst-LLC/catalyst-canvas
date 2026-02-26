# app/__init__.py
from flask import Flask, redirect, url_for
from .routes import bp as core_bp
def create_app:
 app = Flask(__name__)
 app.config["SECRET_KEY"] = "dev" # or pull from env in production
 # Register your blueprint
 app.register_blueprint(core_bp)
 # Optional: set home to global empathize (or swap to 'core.index')
 @app.route("/")
 def home:
 return redirect(url_for("core.empathize_root")) # or: url_for("core.index")
 return app
