import schema

def add_project(params):
    project = schema.Projects(status=params["status"],name=params["name"],description=params["description"])
    schema.add(project)
    print("Project added")
    # TODO: Implement notification about change


## Example usage
project = {
        "name":"SIPB Minecraft",
        "status":"active",
        "description":"Virtual MIT in a Minecraft server!"
        }

add_project(project)
