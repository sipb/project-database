// Based on https://stackoverflow.com/questions/14853779/adding-input-elements-dynamically-to-form

// Global counter to obtain unique role field names:
var role_counter = 0;

function add_role(role_name="", role_description="", role_prereqs="") {
    var container = document.getElementById("roles_container");
    var role_fields = document.createElement("p");
    role_fields.setAttribute(
        "style",
        "border:1px; border-style:solid; border-color:#000000; padding:1em;"
    );

    var role_name_label = document.createElement("label");
    role_name_label.setAttribute("for", "role_name");
    role_name_label.innerHTML = "Role name: ";
    role_fields.appendChild(role_name_label);

    var role_name_field = document.createElement("input");
    role_name_field.setAttribute("type", "text");
    role_name_field.setAttribute("id", "role_name");
    role_name_field.setAttribute("name", "role_name_" + role_counter);
    role_name_field.setAttribute("value", role_name);
    role_fields.appendChild(role_name_field);

    role_fields.appendChild(document.createElement("br"));

    var role_description_label = document.createElement("label");
    role_description_label.setAttribute("for", "role_description");
    role_description_label.innerHTML = "Role description:";
    role_fields.appendChild(role_description_label);

    role_fields.appendChild(document.createElement("br"));

    var role_description_field = document.createElement("textarea");
    role_description_field.setAttribute("id", "role_description");
    role_description_field.setAttribute(
        "name", "role_description_" + role_counter
    );
    role_description_field.setAttribute("rows", "4");
    role_description_field.setAttribute("cols", "80");
    role_description_field.value = role_description;
    role_fields.appendChild(role_description_field);

    role_fields.appendChild(document.createElement("br"));

    var role_prereqs_label = document.createElement("label");
    role_prereqs_label.setAttribute("for", "role_prereqs");
    role_prereqs_label.innerHTML = "Role prereqs:"
    role_fields.appendChild(role_prereqs_label);

    role_fields.appendChild(document.createElement("br"));

    var role_prereqs_field = document.createElement("textarea");
    role_prereqs_field.setAttribute("type", "text");
    role_prereqs_field.setAttribute("id", "role_prereqs");
    role_prereqs_field.setAttribute(
        "name", "role_prereqs_" + role_counter
    );
    role_prereqs_field.setAttribute("rows", "4");
    role_prereqs_field.setAttribute("cols", "80");
    role_prereqs_field.value = role_prereqs;
    role_fields.appendChild(role_prereqs_field);

    role_fields.appendChild(document.createElement("br"));

    var remove_role_button = document.createElement("input");
    remove_role_button.setAttribute("type", "button");
    remove_role_button.setAttribute("value", "Remove role");
    remove_role_button.setAttribute("onclick", "remove_role(this)");
    role_fields.appendChild(remove_role_button);

    container.appendChild(role_fields);

    role_counter = role_counter + 1;
}

function remove_role(elem) {
    elem.parentElement.remove();
}
