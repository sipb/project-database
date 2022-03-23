// Based on https://stackoverflow.com/questions/14853779/adding-input-elements-dynamically-to-form

// Global counter to obtain unique role field names:
var role_counter = 0;

function add_role() {
    var container = document.getElementById("roles_container");
    var role_fields = document.createElement("p");

    var role_name_label = document.createElement("label");
    role_name_label.setAttribute("for", "role_name");
    role_name_label.innerHTML = "Role name:"
    role_fields.appendChild(role_name_label);

    var role_name_field = document.createElement("input");
    role_name_field.setAttribute("type", "text");
    role_name_field.setAttribute("id", "role_name");
    role_name_field.setAttribute("name", "role_name_" + role_counter);
    role_fields.appendChild(role_name_field);

    role_fields.appendChild(document.createElement("br"));

    var role_description_label = document.createElement("label");
    role_description_label.setAttribute("for", "role_description");
    role_description_label.innerHTML = "Role description:"
    role_fields.appendChild(role_description_label);

    var role_description_field = document.createElement("input");
    role_description_field.setAttribute("type", "text");
    role_description_field.setAttribute("id", "role_description");
    role_description_field.setAttribute(
        "name", "role_description_" + role_counter
    );
    role_fields.appendChild(role_description_field);

    role_fields.appendChild(document.createElement("br"));

    var role_prereqs_label = document.createElement("label");
    role_prereqs_label.setAttribute("for", "role_prereqs");
    role_prereqs_label.innerHTML = "Role prereqs:"
    role_fields.appendChild(role_prereqs_label);

    var role_prereqs_field = document.createElement("input");
    role_prereqs_field.setAttribute("type", "text");
    role_prereqs_field.setAttribute("id", "role_prereqs");
    role_prereqs_field.setAttribute(
        "name", "role_prereqs_" + role_counter
    );
    role_fields.appendChild(role_prereqs_field);

    role_fields.appendChild(document.createElement("br"));

    var remove_roll_button = document.createElement("input");
    remove_roll_button.setAttribute("type", "button");
    remove_roll_button.setAttribute("value", "Remove role");
    remove_roll_button.setAttribute("onclick", "remove_role(this)");
    role_fields.appendChild(remove_roll_button);

    container.appendChild(role_fields);

    role_counter = role_counter + 1;
}

function remove_role(elem) {
    elem.parentElement.remove();
}
