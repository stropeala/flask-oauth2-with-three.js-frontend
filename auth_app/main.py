from flask import Blueprint, render_template
from flask_login import current_user

# Main blueprint setup
main = Blueprint("main", __name__)


@main.route("/")
def index():
    if current_user.is_authenticated:
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email, current_user.profile_pic
            )
        )
    else:
        return '<a class = "Button" href="/login">Google Login</a>'


@main.route("/test")
def test():
    return render_template("auth_frontend/index.html", user=current_user)
