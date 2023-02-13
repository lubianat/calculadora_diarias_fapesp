""" A flask app to connect iNaturalist to Wikidata."""

from email.policy import default
from flask_bootstrap import Bootstrap5

import flask
from flask import (
    Flask,
    jsonify,
    flash,
    render_template,
    request,
    send_from_directory,
    redirect,
)
from fapesp_calculator.calculate_international import *
from fapesp_calculator.calculate_national import *

from fapesp_calculator.por_extenso import data_por_extenso
import os
from pathlib import Path
import requests
from config import Config
from forms import *


APP = Path(__file__).parent.resolve()


international_values_dict = json.loads(
    RESULTS.joinpath("fapesp_international_values.json").read_text(encoding="UTF-8")
)

international_values_dict_computable = {}

for country_for_dict, country_data in international_values_dict.items():
    international_values_dict_computable[country_for_dict] = dict()

    for location_for_dict, value in country_data.items():
        international_values_dict_computable[country_for_dict][
            location_for_dict
        ] = Money(value.replace(",", "."), Currency.USD)

app = Flask(__name__)

app.config.from_object(Config)
Bootstrap5(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "uploads"

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index_base():
    return flask.render_template("index.html")


@app.route("/index")
def index():
    return flask.render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
@app.route("/login")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(
            "Login requested for user {}, remember_me={}".format(
                form.username.data, form.remember_me.data
            )
        )
        return redirect("/index")
    return render_template("login.html", title="Sign In", form=form)


@app.route("/internacional/", methods=["GET", "POST"])
@app.route("/internacional", methods=["GET", "POST"])
def internacional():
    form = dailyStipendInternationalForm()
    form.location.choices = [
        (a, a) for a in list(international_values_dict_computable["Albânia"].keys())
    ]

    if request.method == "POST":

        print("RUNNING CODE")
        my_dict = {}
        if form.plus_day.data == "sim":
            extra_day = True
        else:
            extra_day = False

        message_to_send = generate_template_for_international_event(
            my_dict=my_dict,
            event_start_date_time=form.event_start_date.data,
            event_end_date_time=form.event_end_date.data,
            extra_day=extra_day,
            country=form.country.data,
            subnational_location=form.location.data,
            filled_template_path=APP.joinpath("uploads/modelo_preenchido.docx"),
        )

        return render_template(
            "internacional.html",
            submitted=True,
            form=form,
            message_to_send=message_to_send,
            location=form.location.data,
            country=form.country.data,
            daily_stipend=international_values_dict_computable[form.country.data][
                form.location.data
            ],
        )

    return render_template("internacional.html", submitted=False, form=form)


@app.route("/location/<country>")
def location(country):
    locations = [
        {"name": a} for a in list(international_values_dict_computable[country].keys())
    ]
    return jsonify({"locations": locations})


@app.route("/nacional/", methods=["GET", "POST"])
@app.route("/nacional", methods=["GET", "POST"])
def nacional():
    form = dailyStipendNationalForm()

    if form.validate_on_submit():
        my_dict = {}
        if form.plus_day.data == "sim":
            extra_day = True
        else:
            extra_day = False

        if form.level.data == "base":
            message_to_send = generate_template_for_national_event(
                my_dict=my_dict,
                event_start_date_time=form.event_start_date.data,
                event_end_date_time=form.event_end_date.data,
                extra_day=extra_day,
                filled_template_path=APP.joinpath("uploads/modelo_preenchido.docx"),
            )
        if form.level.data == "plus":
            message_to_send = generate_template_for_national_event(
                my_dict=my_dict,
                event_start_date_time=form.event_start_date.data,
                event_end_date_time=form.event_end_date.data,
                category="Pesquisadores, dirigentes, coordenadores, assessores, conselheiros e pós-doutorandos",
                subcategory="Com pernoite (em capitais de Estado, Angra dos Reis (RJ), Brasília (DF), Búzios (RJ) e Guarujá (SP)",
                extra_day=extra_day,
                filled_template_path=APP.joinpath("uploads/modelo_preenchido.docx"),
            )

        return render_template(
            "nacional.html",
            submitted=True,
            form=form,
            message_to_send=message_to_send,
        )

    return render_template("nacional.html", submitted=False, form=form)


@app.route("/about")
def about():
    return flask.render_template("about.html")


@app.route("/uploads/<path:filename>", methods=["GET", "POST"])
def download(filename):
    # Appending app path to upload folder path within app root folder
    uploads = os.path.join(app.root_path, app.config["UPLOAD_FOLDER"])

    # Returning file from appended path
    return send_from_directory(directory=uploads, path=filename)
