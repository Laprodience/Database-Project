from flask import Flask, render_template
import view
import os
from flask import current_app as app

def create_app():
    app = Flask(__name__)
    app.add_url_rule("/", view_func=view.login_page, methods=["GET", "POST"])
    app.add_url_rule("/register", view_func=view.register_page, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=view.logout_page, methods=["GET", "POST"])
    app.add_url_rule("/home", view_func=view.home_page)

    app.config.from_object("settings")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)