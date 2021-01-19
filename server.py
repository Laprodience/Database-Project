from flask import Flask, render_template
import view
import os
from flask import current_app as app

def create_app():
    app = Flask(__name__)
    app.add_url_rule("/", view_func=view.login_page, methods=["GET", "POST"])
    app.add_url_rule("/register", view_func=view.register_page, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=view.logout_page, methods=["GET", "POST"])
    app.add_url_rule("/home", view_func=view.home_page, methods=["GET", "POST"])
    app.add_url_rule("/matches", view_func=view.matches_page, methods=["GET", "POST"])
    app.add_url_rule("/teams", view_func=view.teams_page, methods=["GET", "POST"])
    app.add_url_rule("/profile", view_func=view.profile_page, methods=["GET", "POST"])
    app.add_url_rule("/users", view_func=view.users_page, methods=["GET", "POST"])
    app.add_url_rule("/top", view_func=view.top_page, methods=["GET", "POST"])
    app.add_url_rule("/panel", view_func=view.admin_page, methods=["GET", "POST"])
    app.add_url_rule("/player/<player_nickname>", view_func=view.player_page, methods=["GET", "POST"])

    app.config.from_object("settings")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)