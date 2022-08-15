import os, shutil, sys, traceback

from .utils import *
from pkg_resources import Requirement, resource_filename
from .version import __version__

help_message = '''
    tdbuild, version {}
    a simple build tool for c/c++ projects
    usage:
        tdbuild new, to initialize a new project
        tdbuild setup, to run project setup
        tdbuild prebuild, to run prebuild
        tdbuild build, to run prebuild + build
        tdbuild run, to run the executable
'''.format(__version__)

def new_project():
    here = os.getcwd()
    template = resource_filename(Requirement.parse("tdbuild"), os.path.join("tdbuild", "template.py"))
    shutil.copy(template, os.path.join(os.getcwd(), "tdfile.py"))
    print_info(f'New project initialized in {here}. Add configurations to tdfile.py to get started!')
        
def main():
    if len(sys.argv) == 2 and sys.argv[1] == "version":
        print(help_message)
        return
    if len(sys.argv) == 2 and sys.argv[1] == "help":
        print(help_message)
        return        
        
    if len(sys.argv) == 2 and sys.argv[1] == "new":
        new_project()
        return
        
    import tdfile
    try:
        sys.path.append(os.getcwd())
        import tdfile

        builder = tdfile.Builder()
        builder.build_options = tdfile.build_options
    except SyntaxError as syntax_error:
        print(traceback.format_exc())
        return
    except BaseException as error:
        print('Tried to call build(), but no tdfile was found. Did you initialize a project with tdbuild new?')
        return
        
    
    if len(sys.argv) == 1 or sys.argv[1] == "build":
        builder.build()
    elif sys.argv[1] == "run":
        builder.run()
    else:
        method = getattr(builder, sys.argv[1])
        method()
        
if __name__ == "__main__":
    main()
