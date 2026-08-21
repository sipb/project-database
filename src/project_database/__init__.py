from flask import Flask, Response, request, send_from_directory

from . import (
    addproject,
    approveproject,
    confirmproject,
    editproject,
    faq,
    performaddproject,
    performapproveproject,
    performconfirmproject,
    performeditproject,
    performrollback,
    projecthistory,
    projectjson,
    projectlist,
    templateutils,
)

app = Flask(__name__)


@app.route("/templates/<path:filename>")
def route_static_templates(filename):
    return send_from_directory(templateutils.TEMPLATES_DIR, filename)


@app.route("/addproject.py")
def route_addproject():
    return Response(addproject.view(), mimetype="text/html")


@app.route("/approveproject.py")
def route_approveproject():
    return Response(approveproject.view(request.values), mimetype="text/html")


@app.route("/confirmproject.py")
def route_confirmproject():
    return Response(confirmproject.view(request.values), mimetype="text/html")


@app.route("/editproject.py")
def route_editproject():
    return Response(editproject.view(request.values), mimetype="text/html")


@app.route("/faq.py")
def route_faq():
    return Response(faq.view(), mimetype="text/html")


@app.route("/performaddproject.py", methods=["POST"])
def route_performaddproject():
    return Response(performaddproject.view(request.values), mimetype="text/html")


@app.route("/performapproveproject.py", methods=["POST"])
def route_performapproveproject():
    return Response(performapproveproject.view(request.values), mimetype="text/html")


@app.route("/performconfirmproject.py", methods=["POST"])
def route_performconfirmproject():
    return Response(performconfirmproject.view(request.values), mimetype="text/html")


@app.route("/performeditproject.py", methods=["POST"])
def route_performeditproject():
    return Response(performeditproject.view(request.values), mimetype="text/html")


@app.route("/performrollback.py")
def route_performrollback():
    return Response(performrollback.view(request.values), mimetype="text/html")


@app.route("/projecthistory.py")
def route_projecthistory():
    return Response(projecthistory.view(request.values), mimetype="text/html")


@app.route("/projectjson.py")
def route_projectjson():
    return Response(projectjson.view(), mimetype="application/json")


@app.route("/projectlist.py")
def route_projectlist():
    return Response(projectlist.view(request.values), mimetype="text/html")


@app.route("/")
def route_index():
    return route_projectlist()


def main():
    """Run the dev server"""
    # TODO: Run sendreminders every hour
    app.run(debug=True)
