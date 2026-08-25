from . import strutils


def contact_list_to_dict_list(contact_list):
    """Convert a list of contacts to a properly-formatted list of dicts.

    The first entry is assumed to be the primary contact.

    Parameters
    ----------
    contact_list : list of str
        The email addresses for each contact.

    Returns
    -------
    contact_dict_list : list of dict
        The formatted contact dicts with types assigned.
    """
    result = []
    idx = 0
    for contact in contact_list:
        if len(contact) > 0:
            result.append({"email": contact, "type": "secondary", "index": idx})
            idx += 1

    if len(result) > 0:
        result[0]["type"] = "primary"
    return result


def get_role_ids(arguments):
    """Get all role IDs from the arguments from CGI.

    Parameters
    ----------
    arguments : werkzeug.datastructures.MultiDict
        The combined query string and form data from the request.

    Returns
    -------
    role_ids : list of int
        The sorted role IDs present in the arguments.
    """
    role_ids = set()
    for key in arguments:
        # Check all fields so that we can catch mal-formed inputs:
        if key.startswith("role_name_"):
            role_ids.add(int(key[len("role_name_") :]))
        elif key.startswith("role_description_"):
            role_ids.add(int(key[len("role_description_") :]))
        elif key.startswith("role_prereqs_"):
            role_ids.add(int(key[len("role_prereqs_") :]))
    return sorted(role_ids)


def get_link_ids(arguments):
    """Get all link IDs from the arguments from CGI.

    Parameters
    ----------
    arguments : werkzeug.datastructures.MultiDict
        The combined query string and form data from the request.

    Returns
    -------
    link_ids : list of int
        The sorted link IDs present in the arguments.
    """
    link_ids = set()
    for key in arguments:
        # Check all fields so that we can catch mal-formed inputs:
        if key.startswith("link_"):
            link_ids.add(int(key[len("link_") :]))
        elif key.startswith("anchortext_"):
            link_ids.add(int(key[len("anchortext_") :]))
    return sorted(link_ids)


def extract_roles(arguments):
    """Extract the role dicts from the arguments from CGI.

    Parameters
    ----------
    arguments : werkzeug.datastructures.MultiDict
        The combined query string and form data from the request.

    Returns
    -------
    roles : list of dict
        The information for each role.
    """
    role_ids = get_role_ids(arguments)
    roles = []
    for index, role_id in enumerate(role_ids):
        roles.append(
            {
                "role": arguments.get(f"role_name_{role_id}", ""),
                "description": arguments.get(f"role_description_{role_id}", ""),
                "prereq": arguments.get(f"role_prereqs_{role_id}", ""),
                "index": index,
            }
        )
        if len(roles[-1]["prereq"]) == 0:
            roles[-1]["prereq"] = None
    return roles


def extract_links(arguments):
    """Extract the link dicts from the arguments from CGI.

    Parameters
    ----------
    arguments : werkzeug.datastructures.MultiDict
        The combined query string and form data from the request.

    Returns
    -------
    links : list of dict
        The information for each link.
    """
    link_ids = get_link_ids(arguments)
    links = []
    for index, link_id in enumerate(link_ids):
        links.append(
            {
                "link": strutils.make_url_absolute(
                    arguments.get(f"link_{link_id}", "")
                ),
                "anchortext": arguments.get(f"anchortext_{link_id}", ""),
                "index": index,
            }
        )
        if len(links[-1]["anchortext"]) == 0:
            links[-1]["anchortext"] = None
    return links


def index_dictify_list(str_list, key):
    """Convert a list of strings to a list of dicts with index fields.

    Parameters
    ----------
    str_list : list of str
        The strings to index-dictify.
    key : str
        The key to use for the values from str_list.

    Returns
    -------
    dict_list : list of dict
        The wrapped values from str_list.
    """
    return [{key: value, "index": index} for index, value in enumerate(str_list)]


def new_member_form_to_dict(arguments):
    """Reformat the arguments from CGI into a new member form submission
    dict.

    Parameters
    ----------
    arguments : werkzeug.datastructures.MultiDict
        The combined query string and form data from the request.

    Returns
    -------
    submission_info : dict
        The new member form submission info dict.
    """
    return {
        "interests": arguments.getlist("interests"),
        "interests_other": arguments.get("interests_other", "").strip(),
        "experience_level": arguments.get("experience_level", ""),
        "experience_details": arguments.get("experience_details", "").strip(),
        "comments": arguments.get("comments", "").strip(),
    }


def suggested_project_ids_from_arguments(arguments):
    """Get the list of suggested project IDs from the arguments from CGI.

    Parameters
    ----------
    arguments : werkzeug.datastructures.MultiDict
        The combined query string and form data from the request.

    Returns
    -------
    project_ids : list of int
        The selected project IDs.
    """
    return [int(project_id) for project_id in arguments.getlist("suggested_projects")]


def args_to_dict(arguments):
    """Reformat the arguments from CGI into a dict.

    Parameters
    ----------
    arguments : werkzeug.datastructures.MultiDict
        The combined query string and form data from the request.

    Returns
    -------
    project_info : dict
        The project info dict.
    """
    return {
        "name": arguments.get("name", ""),
        "description": arguments.get("description", ""),
        "status": arguments.get("status", ""),
        "links": extract_links(arguments),
        "comm_channels": index_dictify_list(
            strutils.split_comma_sep(arguments.get("comm_channels", "")),
            "commchannel",
        ),
        "contacts": contact_list_to_dict_list(
            strutils.split_comma_sep(arguments.get("contacts", ""))
        ),
        "roles": extract_roles(arguments),
    }
