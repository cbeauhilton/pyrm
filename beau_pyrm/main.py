import typer
import json
import pathlib
import dateparser

# default file locations

home_dir = pathlib.Path.home()
default_json_path = home_dir / ".local/pyrm/pyrm.json"
default_config_file = home_dir / ".config/pyrm/pyrmrc"

beau_contact = [{
    "fullname": "Beau Hilton",
    "firstname": "Beau",
    "lastname": "Hilton",
    "postnominals": "MD",
    "email": "cbeauhilton@gmail.com",
}]

app = typer.Typer()


@app.callback()
def callback():
    """
    Welcome to PyRM, a very simple personal relationship manager, 
    written in Python, 
    with a JSON default backend.
    """

# load json db file

def jsondump(db):
    with open(default_json_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

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
        d = {"fullname": fullname,
            "firstname": firstname,
            "lastname": lastname,
            "postnominals": postnominals,
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
    jsondump(db)



# @app.command()
# def init(file_location: str = typer.Argument(file_location), file_name: str = typer.Argument(file_name)):
#     """
#     Creates a json file if it doesn't exist.
#     Defaults to "~/.local/pyrm/pyrm.json".
#     If desired, specify new --file_location and/or --file_name.
#     Be aware that pathlib does not automatically expand "~".
#     This will also create a config file at ~/.config/pyrm/pyrmrc.
#     There is not yet an option to change the location of this config.
#     """
#     p = pathlib.Path(file_location)
#     full_path = p / file_name
# 
#     if not os.path.exists(full_path):
#         p.mkdir(parents=True, exist_ok=True) 
#         open(full_path, 'w').close()
# 
#         os.makedirs(os.path.dirname(default_config_file), exist_ok=True)
#         with open(default_config_file, "w") as f:
#             print(f"{full_path}", file=f)
# 
#         typer.echo(f"Created empty PyRM file at {full_path}.")
# 
#     else:
#         typer.echo(f"PyRM file already exists at {full_path}.")

# try:
#     with open(default_config_file) as f:
#         json_file = f.read()
# except FileNotFoundError:
#     print(f"{default_config_file} does not yet exist. Making it now..." )
#     os.makedirs(os.path.dirname(default_config_file), exist_ok=True)
#     with open(default_config_file, "w") as f:
#         print(f"{default_json_path}", file=f)

