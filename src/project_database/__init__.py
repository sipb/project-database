import os
import secrets

from flask import Flask, Response, abort, redirect, request, send_from_directory

from .routes import (
    addproject,
    approveproject,
    authdebug,
    confirmproject,
    editproject,
    faq,
    newmemberform,
    newmemberreview,
    performaddproject,
    performapproveproject,
    performconfirmproject,
    performeditproject,
    performnewmemberform,
    performrespondnewmember,
    performrollback,
    projecthistory,
    projectjson,
    projectlist,
    respondnewmember,
)
from .services import sendreminders as sendreminders
from .utils import templateutils

app = Flask(__name__)

debug = os.environ.get("FLASK_DEBUG", "0") == "1"
app.config["DEBUG"] = debug
print("DEBUG =", debug)

app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")
if app.config["SECRET_KEY"] is None:
    app.config["SECRET_KEY"] = secrets.token_hex(32)

@app.route("/templates/<path:filename>")
def route_static_templates(filename):
    return send_from_directory(templateutils.TEMPLATES_DIR, filename)


@app.route("/addproject")
def route_addproject():
    return Response(addproject.view(), mimetype="text/html")


@app.route("/approveproject")
def route_approveproject():
    return Response(approveproject.view(request.values), mimetype="text/html")


@app.route("/confirmproject")
def route_confirmproject():
    return Response(confirmproject.view(request.values), mimetype="text/html")


@app.route("/editproject")
def route_editproject():
    return Response(editproject.view(request.values), mimetype="text/html")


@app.route("/faq")
def route_faq():
    return Response(faq.view(), mimetype="text/html")


@app.route("/newmemberform")
def route_newmemberform():
    return Response(newmemberform.view(), mimetype="text/html")


@app.route("/performnewmemberform", methods=["POST"])
def route_performnewmemberform():
    return Response(performnewmemberform.view(request.values), mimetype="text/html")


@app.route("/newmemberreview")
def route_newmemberreview():
    return Response(newmemberreview.view(), mimetype="text/html")


@app.route("/respondnewmember")
def route_respondnewmember():
    return Response(respondnewmember.view(request.values), mimetype="text/html")


@app.route("/performrespondnewmember", methods=["POST"])
def route_performrespondnewmember():
    return Response(
        performrespondnewmember.view(request.values), mimetype="text/html"
    )


@app.route("/performaddproject", methods=["POST"])
def route_performaddproject():
    return Response(performaddproject.view(request.values), mimetype="text/html")


@app.route("/performapproveproject", methods=["POST"])
def route_performapproveproject():
    return Response(performapproveproject.view(request.values), mimetype="text/html")


@app.route("/performconfirmproject", methods=["POST"])
def route_performconfirmproject():
    return Response(performconfirmproject.view(request.values), mimetype="text/html")


@app.route("/performeditproject", methods=["POST"])
def route_performeditproject():
    return Response(performeditproject.view(request.values), mimetype="text/html")


@app.route("/performrollback")
def route_performrollback():
    return Response(performrollback.view(request.values), mimetype="text/html")


@app.route("/projecthistory")
def route_projecthistory():
    return Response(projecthistory.view(request.values), mimetype="text/html")


@app.route("/projectjson")
def route_projectjson():
    return Response(projectjson.view(), mimetype="application/json")


@app.route("/projectlist")
def route_projectlist():
    print(request.values)
    return Response(projectlist.view(request.values), mimetype="text/html")


@app.route("/")
def route_index():
    return route_projectlist()

@app.route("/authdebug", methods=["GET", "POST"])
def route_authdebug():
    if not app.debug:
        abort(404)
    
    action = request.values.get("action", "login")
    if request.method == "POST":
        email = (request.form.get("debugemail") or "").strip().lower()
        from flask import session

        if email.count("@") != 1 or not email.endswith("@mit.edu"):
            abort(400)

        session["debug_email"] = email
        return redirect("/projectlist")
    
    if action == "logout":
        from flask import session
        session.pop("debug_email", None)
        return redirect("/projectlist")
    
    return Response(authdebug.view(), mimetype="text/html")


@app.route("/hlogin")
def route_login():
    return redirect("/")


@app.route("/hlogout")
def route_logout():
    return redirect("/")


def main():
    """Run the dev server"""
    # TODO: Run sendreminders every hour
    app.run(debug=debug)
