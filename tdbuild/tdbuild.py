# TODO:
# binary_type
# defines on all platforms
# update template
# make most fields optional
# return to calling dir after building
# private functions

import os, subprocess, sys, re, shutil, platform, colorama
from pkg_resources import Requirement, resource_filename

# @hack: I hate Python modules
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import __version__
version = __version__.__version__

TEMPLATE_PATH = resource_filename(Requirement.parse("tdbuild"), os.path.join("tdbuild", "tdfile.template"))

help_message = '''
    tdbuild, version {}
    a simple build tool for c/c++ projects
    usage:
        tdbuild new, to initialize a new project
        tdbuild setup, to run project setup
        tdbuild prebuild, to run prebuild
        tdbuild build, to run prebuild + build
        tdbuild run, to run the executable
'''.format(version)

colorama.init()

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

# Base builder class. Reads in configurations, generates a compiler command, executes it. Provides
# 'virtual' methods you can override. 
class base_builder():
    def __init__(self):
        self.build_options = None
        self.build_cmd = ""
        self.project_root = os.getcwd()

    def absolute_path(self, path_elements):
        return os.path.join(self.project_root, *path_elements)
    
    def add_unix_source(self):
        for source in self.build_options['source_files']:
            absolute_source_file = os.path.join(self.project_root, self.build_options['source_dir'], source)
            absolute_source_file = os.path.realpath(absolute_source_file)
            self.push(absolute_source_file)
            
    def add_unix_includes(self):
        for include in self.build_options['include_dirs']:
            absolute_include_dir = os.path.join(self.project_root, include)
            absolute_include_dir = os.path.realpath(absolute_include_dir)
            self.push("-I" + absolute_include_dir)
            
    def add_unix_cpp(self):
        self.push("-std=c++{}".format(self.build_options['cpp_standard']))


    def push(self, item):
        self.build_cmd = self.build_cmd + item + " "

    def prebuild(self):
        print_warning("Calling prebuild, but no prebuild step was defined.")
        
    def build(self):
        print_info("Running from {}".format(os.getcwd()))
        print_info("Project root is {}".format(self.project_root))
        if platform.system() == 'Windows':
            self.build_windows()
        elif platform.system() == 'Darwin':
            self.build_mac()
        elif platform.system() == 'Linux':
            self.build_linux()

    def build_linux(self):
        # Set up default options.
        if 'defines' not in self.build_options:
            self.build_options['defines'] = []

        if 'cpp' not in self.build_options['Linux']:
            self.build_options['Linux']['cpp'] = True

        if 'compiler' not in self.build_options['Linux']:
            if self.build_options['Linux']['cpp']:
                self.build_options['Linux']['compiler'] = 'g++'
            else:
                self.build_options['Linux']['compiler'] = 'gcc'
                
        compiler = self.build_options['Linux']['compiler']
            
        # Find the path to the compiler using 'which'
        process = subprocess.Popen(['which', compiler], stdout=subprocess.PIPE)
        compiler_path, err = process.communicate()
        compiler_path = compiler_path.decode('UTF-8').strip()
        if err or not compiler_path:
            print_error("tried to find your compiler using 'which {}', but it returned an error.".format(self.build_options['Linux']['compiler']))
            exit()
            
        self.push(compiler_path)
        
        if self.build_options['cpp']:
            self.add_unix_cpp()
            
        if self.build_options['debug']:
            self.push("-g")

        for define in self.build_options['defines']:
            self.push('-D {}'.format(define))
            
        if 'binary_type' in self.build_options:
            binary_type = self.build_options['binary_type']
            if binary_type == 'shared_library':
                self.push('-shared')
            
        for extra in self.build_options['Linux']['extras']:
            self.push(extra)

        self.add_unix_source()
        self.add_unix_includes()
            
        self.push('-o ' + self.build_options['Linux']['out'])

        for lib in self.build_options['Linux']['user_libs']:
            self.push('-l' + lib)

        for lib in self.build_options['Linux']['system_libs']:
            self.push('-l' + lib)

        print_info("Generated compiler command:")
        print(self.build_cmd)
        print_info("Compiling...")

        make_cd_build_dir(self.build_options['build_dir'])

        process = subprocess.Popen(self.build_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        compiler_messages, err = process.communicate()
        compiler_messages = compiler_messages.decode('UTF-8').split('\n')
        err = err.decode('UTF-8').split('\n')

        if actually_has_message(compiler_messages):
            print_info("Compiler messages:")
            for message in compiler_messages:
                print_info(message)

        compile_error = False
        compile_warning = False
        if actually_has_message(err):
            print_info("Compiler warnings + errors:")
            
            for message in err:
                if message == '':
                    continue
                elif 'error' in message:
                    print_error(message)
                    compile_error = True
                    # Maybe printing everything else as a warning is Not Smart, but our heuristic for whether a line is an error is...lacking.
                else:
                    print_warning(message)
                    compile_warning = True


            if compile_error or compile_warning:
                print("")
            
        if compile_error:
            print(colorama.Fore.RED + "[BUILD FAILED]")
        else:
            print(colorama.Fore.GREEN + "[BUILD SUCCESSFUL]")

    def build_mac(self):
        # Find the path to the compiler using 'which'
        compiler = self.build_options['Darwin']['compiler']
        process = subprocess.Popen(['which', compiler], stdout=subprocess.PIPE)
        compiler_path, err = process.communicate()
        compiler_path = compiler_path.decode('UTF-8').strip()
        if err or not compiler_path:
            print_error("tried to find your compiler using 'which {}', but it returned an error.".format(self.build_options['Darwin']['compiler']))
            exit()
            
        self.push(compiler_path)


        if self.build_options['debug']:
            self.push("-g")

        for extra in self.build_options['Darwin']['extras']:
            self.push(extra)
            
        if self.build_options['cpp']:
            self.add_unix_cpp()

        self.add_unix_source()
        self.add_unix_includes()

        for lib in self.build_options['Darwin']['user_libs']:
            absolute_lib_path = os.path.join(self.project_root, self.build_options['lib_dir'], lib)
            absolute_lib_path = os.path.realpath(absolute_lib_path)
            self.push(absolute_lib_path)

        for lib in self.build_options['Darwin']['system_libs']:
            self.push('-l' + lib)

        for framework in self.build_options['Darwin']['frameworks']:
            self.push('-framework ' + framework)

        self.push('-o ' + self.build_options['Darwin']['out'])
        
        print_info("Generated compiler command:")
        print(self.build_cmd)
        print_info("Invoking the compiler")

        make_cd_build_dir(self.build_options['build_dir'])

        process = subprocess.Popen(self.build_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        compiler_messages, err = process.communicate()
        compiler_messages = compiler_messages.decode('UTF-8').split('\n')
        err = err.decode('UTF-8').split('\n')
        
        compile_error = False
        compile_warning = False
        for message in err:
            if 'error' in message:
                print_error(message)
                compile_error = True
            elif 'warning' in message:
                print_warning(message)
                compile_warning = True

        if compile_error or compile_warning:
            print("")
            
        if compile_error:
            print(colorama.Fore.RED + "[BUILD FAILED]")
        else:
            print(colorama.Fore.GREEN + "[BUILD SUCCESSFUL]")

    def build_windows(self):
        win_options = self.build_options['Windows']
        self.push("cl.exe")

        for extra in self.build_options['Windows']['extras']:
            self.push(extra)

        if self.build_options['cpp']:
            self.push("/TP")
            self.push("/std:c++{}".format(self.build_options['cpp_standard']))
        else:
            self.push("/TC")

        if self.build_options['debug']:
            self.push("-Zi")

        for warning in self.build_options['Windows']['warnings']:
            self.push("/wd{}".format(warning))

        if win_options['runtime_library']:
            self.push("/" + self.build_options['Windows']['runtime_library'])

        for source_file in self.build_options['source_files']:
            absolute_source_file = os.path.join(self.project_root, self.build_options['source_dir'], source_file)
            self.push(quote(absolute_source_file))

        for include_dir in self.build_options['include_dirs']:
            absolute_include_dir = os.path.join(self.project_root, include_dir)
            self.push('/I{}'.format(quote(absolute_include_dir)))

        if 'defines' in self.build_options:
            for define in self.build_options['defines']:
                self.push('/D{}'.format(define))

        if 'binary_type' in self.build_options:
            binary_type = self.build_options['binary_type']
            if binary_type == 'shared_library':
                self.push('/LD')
                
        self.push("/link")
        self.push("/verbose:lib")
        for system_lib in self.build_options['Windows']['system_libs']:
            self.push(system_lib)

        for user_lib in self.build_options['Windows']['user_libs']:
            absolute_lib_dir = os.path.join(self.project_root, self.build_options['lib_dir'], user_lib)
            self.push(quote(absolute_lib_dir))

        if not self.build_options['show_console']:
            self.push('/SUBSYSTEM:windows')
            self.push('/ENTRY:mainCRTStartup')
            
        for ignore in self.build_options['Windows']['ignore']:
            self.push("/ignore:" + ignore)

        if 'arch' in self.build_options['Windows']:
            arch = self.build_options['Windows']['arch']
            if arch == 'x86_64':
                self.push("/MACHINE:X64")

        self.push("/out:" + self.build_options['Windows']['out'])

        make_cd_build_dir(self.build_options['build_dir'])

        # Copy DLLs
        if 'dlls' in self.build_options['Windows']:
            for dll in self.build_options['Windows']['dlls']:
                dll_path = os.path.join(self.project_root, self.build_options['lib_dir'], dll)
                shutil.copy(dll_path, os.getcwd())
                print_info("Copied DLL {} to {}".format(dll_path, os.getcwd()))
        
        print_info("Generated compiler command:")
        print_info(self.build_cmd)
        print_info("Invoking the compiler")
        print("")
        
        # @hack: is there a better way to keep a process open?
        process = subprocess.Popen(self.build_cmd, stdout=subprocess.PIPE, env=os.environ.copy())
        compiler_messages, err = process.communicate()
        compiler_messages = compiler_messages.decode('UTF-8').split('\n')
        
        compile_error = False
        compile_warning = False
        for message in compiler_messages:
            if 'error' in message:
                print(colorama.Fore.RED + "[tdbuild] " + colorama.Fore.RESET + message)
                compile_error = True
            elif 'warning' in message:
                print(colorama.Fore.YELLOW + "[tdbuild] " + colorama.Fore.RESET + message)
                compile_warning = True

        os.chdir("..")

        if compile_error or compile_warning:
            print("")
            
        if compile_error:
            print(colorama.Fore.RED + "[BUILD FAILED]" + colorama.Fore.RESET)
        else:
            print(colorama.Fore.GREEN + "[BUILD SUCCESSFUL]" + colorama.Fore.RESET)

        
    def run(self):
        executable = os.path.join(os.getcwd(), self.build_options['build_dir'], self.build_options[platform.system()]['out'])
        subprocess.run([executable]) 
                 
    def setup(self):
        print_warning("Calling setup, but no setup step was defined.")

    def set_output_filename(self, filename):
        self.build_options['Windows']['out'] = '{0}.exe'.format(filename)
        self.build_options['Linux']['out'] = filename
        self.build_options['Darwin']['out'] = filename

    def get_output_filename(self):
        os_options = self.build_options[platform.system()]
        return os_options['out']
        
    def get_output_path(self):
        return os.path.realpath(os.path.join(self.build_options['build_dir'], self.get_output_filename()))

    def get_build_dir(self):
        return os.path.realpath(os.path.join(self.project_root, self.build_options['build_dir']))

def new_project():
    here = os.getcwd()
    shutil.copy(TEMPLATE_PATH, os.path.join(os.getcwd(), "tdfile.py"))
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
        
    try:
        sys.path.append(os.getcwd())
        import tdfile

        builder = tdfile.Builder()
        builder.build_options = tdfile.build_options
    except:
        print('Tried to call build(), but no tdfile was found. Did you initialize a project with tdbuild new?')
        return
        
    
    if len(sys.argv) == 1 or sys.argv[1] == "build":
        builder.prebuild()
        builder.build()
    elif sys.argv[1] == "prebuild":
        builder.prebuild()
    elif sys.argv[1] == "run":
        builder.run()
    elif sys.argv[1] == "setup":
        builder.setup()
    else:
        method = getattr(builder, sys.argv[1])
        method()
        



# Main to let you invoke through the command line. 
if __name__ == "__main__":
    main()
