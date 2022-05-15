// Based on https://stackoverflow.com/questions/14853779/adding-input-elements-dynamically-to-form

// Global counter to obtain unique link field names:
var link_counter = 0;

function add_link(link="", anchortext="") {
    var container = document.getElementById("links_container");
    var link_fields = document.createElement("p");
    link_fields.setAttribute(
        "style",
        "border:1px; border-style:solid; border-color:#000000; padding:1em;"
    );

    var link_label = document.createElement("label");
    link_label.setAttribute("for", "link_" + link_counter);
    link_label.innerHTML = "Link: ";
    link_fields.appendChild(link_label);

    link_fields.appendChild(document.createElement("br"));

    var link_field = document.createElement("input");
    link_field.setAttribute("type", "text");
    link_field.setAttribute("id", "link_" + link_counter);
    link_field.setAttribute("name", "link_" + link_counter);
    link_field.setAttribute("value", link);
    link_field.setAttribute("size", "80");
    link_fields.appendChild(link_field);

    link_fields.appendChild(document.createElement("br"));

    var anchortext_label = document.createElement("label");
    anchortext_label.setAttribute("for", "anchortext_" + link_counter);
    anchortext_label.innerHTML = "Anchor text (optional):";
    link_fields.appendChild(anchortext_label);

    link_fields.appendChild(document.createElement("br"));

    var anchortext_field = document.createElement("input");
    anchortext_field.setAttribute("type", "text");
    anchortext_field.setAttribute("id", "anchortext_" + link_counter);
    anchortext_field.setAttribute("name", "anchortext_" + link_counter);
    anchortext_field.setAttribute("value", link);
    anchortext_field.setAttribute("size", "80");
    link_fields.appendChild(anchortext_field);

    link_fields.appendChild(document.createElement("br"));

    var remove_link_button = document.createElement("input");
    remove_link_button.setAttribute("type", "button");
    remove_link_button.setAttribute("value", "Remove link");
    remove_link_button.setAttribute("onclick", "remove_link(this)");
    link_fields.appendChild(remove_link_button);

    container.appendChild(link_fields);

    link_counter = link_counter + 1;
}

function remove_link(elem) {
    elem.parentElement.remove();
}
