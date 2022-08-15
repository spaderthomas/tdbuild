import os, colorama

def make_cd_build_dir(build_dir):
    build_dir = os.path.join(os.getcwd(), build_dir)
    try:
        os.mkdir(build_dir)
    except:
        pass
    os.chdir(build_dir)

def print_info(message):
    print(colorama.Fore.BLUE + "[info] " + colorama.Fore.RESET + message)

def print_error(message):
    print(colorama.Fore.RED + "[error] " + colorama.Fore.RESET + message)

def print_warning(message):
    print(colorama.Fore.YELLOW + "[warning] " + colorama.Fore.RESET + message)
    
def print_success(message):
    print(colorama.Fore.GREEN + "[success] " + colorama.Fore.RESET + message)
    
def print_prebuild(message):
    print(colorama.Fore.CYAN + "[prebuild] " + colorama.Fore.RESET + message)
    
def quote(string):
    return '"{}"'.format(string)

def trailing_slash(path):
    return os.path.join(path, "")

def actually_has_message(maybe_messages):
    # @hack. Sometimes I'll get a list containing one empty string.
    # It makes my output look ugly, so I hack around it. 
    for maybe_message in maybe_messages:
        if len(maybe_message):
            return True

    return False
