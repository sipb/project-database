from . import templateutils

def view():
    jenv = templateutils.get_jenv()
    
    result = (
        jenv.get_template("authdebug.html")
        .render()
        .encode("utf-8")
    )
    return result