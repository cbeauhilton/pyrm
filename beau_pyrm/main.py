import typer
import json
import pathlib
import dateparser
import datetime

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

# TODO: add interactions, maybe in a subdictionary with datetimes for keys
# TODO: birthdays_coming_up

@app.command()
def birthdays(days: int = typer.Argument(14)):
    """
    list all birthdays that happened/will happen within a given number of days
    """
    #TODO: sort by distance from today
    
    today = datetime.datetime.today()
    margin = datetime.timedelta(days = days)
    for contact in db:
        if "birthday" in contact:
            bday_year = dateparser.parse(contact["birthday"])
            bday_no_year = dateparser.parse(f"{bday_year: %d %B}")
            # if bday_no_year <= today + margin:
            if today - margin <= bday_no_year <= today + margin:
                print(f'{contact["fullname"]} : {contact["birthday"]}')
