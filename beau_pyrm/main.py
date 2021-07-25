import typer
import json
import pathlib
import dateparser
import datetime
import pendulum

# default file locations
# TODO: make these modifiable

home_dir = pathlib.Path.home()
default_json_path = home_dir / ".local/pyrm/pyrm.json"

beau_contact = [
    {
        "fullname": "Beau Hilton",
        "firstname": "Beau",
        "lastname": "Hilton",
        "postnominals": "MD",
        "email_personal": "cbeauhilton@gmail.com",
    }
]

app = typer.Typer()


@app.callback()
def callback():
    """
    Welcome to PyRM,
    a very simple personal relationship manager,
    written in Python.
    """


# helper functions


def date_modified():
    t = datetime.datetime.now()
    date_modified = f"{t:%d %B %Y}"
    return date_modified


def jsondump(db):
    with open(default_json_path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)


# load json db file

try:
    with open(default_json_path) as f:
        db = json.load(f)
        fullnames = []
        for contact in db:
            fullnames.append(contact["fullname"])

except FileNotFoundError:
    print(f"{default_json_path} not found, populating template now...")
    jsondump(beau_contact)
    print("Success. Run it again.")


@app.command()
def add_name(fullname: str, firstname: str, lastname: str, postnominals: str = ""):
    """
    Add the contact's name, as fullname, firstname, lastname, and optionally --postnominals (MD, JD, etc.).
    Using fullname in addition to first and last avoids too much duplication,
    and splitting it automagically is frought with complexity.
    """
    if fullname not in fullnames:
        d = {
            "fullname": fullname,
            "firstname": firstname,
            "lastname": lastname,
            "postnominals": postnominals,
            "contact_added_date": date_modified(),
        }

        typer.echo(d)
        db.append(d)
        jsondump(db)

    else:
        print(f"{fullname} already exists in database.")


@app.command()
def add_birthday(fullname: str, birthday):
    """
    Specify a birthday for an existing contact.
    Uses the dateparser library, so feel free to use any format you like.
    """
    for dict_ in [x for x in db if x["fullname"] == fullname]:
        t = dateparser.parse(birthday)
        dict_["birthday"] = f"{t:%d %B %Y}"
        dict_["contact_modified_date"] = date_modified()
    jsondump(db)


@app.command()
def add_anniversary(fullname: str, anniversary):
    """
    Specify an anniversary for an existing contact.
    Uses the dateparser library, so feel free to use any format you like.
    """
    for dict_ in [x for x in db if x["fullname"] == fullname]:
        t = dateparser.parse(anniversary)
        dict_["anniversary"] = f"{t:%d %B %Y}"
        dict_["contact_modified_date"] = date_modified()
    jsondump(db)


@app.command()
def birthdays(days: int = typer.Argument(365)):
    """
    List all birthdays within a given number of days, ordered by soonest.
    Defaults to showing all birthdays.
    """
    import pandas as pd

    today_dt = pendulum.now()
    coming_soon = {}
    coming_soon["fullname"] = []
    coming_soon["birthday"] = []
    coming_soon["days_until_birthday"] = []

    for contact in db:
        if "birthday" in contact:
            parsed = dateparser.parse(contact["birthday"])
            event_dt = pendulum.instance(parsed).set(year=today_dt.year)
            days_until_event = today_dt.diff(event_dt, False).in_days()
            if days_until_event < 0:
                event_dt = event_dt.add(years=1)
                days_until_event = today_dt.diff(event_dt, False).in_days()

            if days_until_event <= days:
                coming_soon["fullname"].append(contact["fullname"])
                coming_soon["birthday"].append(contact["birthday"])
                coming_soon["days_until_birthday"].append(days_until_event)

    if not coming_soon["fullname"]:
        print(f"No birthdays coming up within {days} days. ")
    else:
        bday_df = (
            pd.DataFrame(coming_soon)
            .sort_values("days_until_birthday")
            .reset_index(drop=True)
        )
        print(bday_df)


# TODO: add interactions (e.g. conversations), maybe in a subdictionary with datetimes for keys
