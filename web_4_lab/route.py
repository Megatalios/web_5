from flask import make_response, render_template, request

from arpakitlib.safely_transfer_to_json import safely_transfer_to_json_str
from web_4_lab.service import get_all_clients, get_client, get_client_by_name, remove_client_by_id, create_client, login_user, register_user
from web_4_lab.utils import get_app


@get_app().route("/all_clients", methods=['GET'])
def route_all_clients():
    return safely_transfer_to_json_str({"clients": get_all_clients()})


@get_app().route("/")
@get_app().route("/index", methods=['GET'])
def route_index():
    return render_template("index.html")


@get_app().route("/about", methods=['GET'])
def route_about():
    return render_template("about_us.html")


@get_app().route('/contacts', methods=['GET'])
def route_contacts():
    return render_template("contacts.html")


@get_app().route('/success', methods=['GET'])
def route_success():
    return render_template("success.html")


@get_app().route('/feedback', methods=['GET'])
def route_feedback():
    return render_template("feedback.html")


@get_app().route('/api/contactrequest/<int:id>', methods=['GET'])
# Получаем запись по id
def route_get_contact_req_by_id(id: int):
    return safely_transfer_to_json_str(get_client(id))


@get_app().route('/api/contactrequest/author/<string:name>', methods=['GET'])
# Получаем запись по имени пользователя
def route_get_client_by_name(name: str):
    name = name.strip()
    if not name:
        return make_response(safely_transfer_to_json_str({"error": "Bad request"}), 400)
    else:
        return make_response(safely_transfer_to_json_str(get_client_by_name(name=name)), 200)


@get_app().route('/api/contactrequest', methods=['POST'])
def route_create_client():
    if (
            not request.json
            or "name" not in request.json
            or "mail" not in request.json
            or "phone_number" not in request.json
            or "message" not in request.json
    ):
        return make_response(safely_transfer_to_json_str({"error": "Not found"}), 404)

    client_data = create_client(
        name=request.json["name"],
        mail=request.json["mail"],
        phone_number=request.json["phone_number"],
        message=request.json["message"]
    )
    return make_response(safely_transfer_to_json_str(client_data), 200)


@get_app().route("/api/contactrequest/<int:id>", methods=["DELETE"])
def route_delete_contact_req_by_id(id: int):
    remove_client_by_id(id)
    return make_response(safely_transfer_to_json_str({'message': "Client was removed"}), 400)


@get_app().route("/notfound", methods=["GET"])
def route_not_found():
    return render_template('404.html', title='404', err={'error': 'Not found', 'code': 404})


# @get_app().route("signed_id", methods=["GET"])
# def signed_in():
#     if (request.cookies['AccountToken'] is not None):
#


@get_app().route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return login_user(request.form)
    return render_template('login.html', title='Login')


@get_app().route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return register_user(request.form)
    return render_template('register.html', title='Register')



def init_routes():
    pass
