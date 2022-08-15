import os, subprocess, sys, re, shutil, platform, colorama
from .utils import *
from .constants import BinaryType


colorama.init()

# Base builder class. Reads in configurations, generates a compiler command, executes it. Provides
# 'virtual' methods you can override. 
class Builder():
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
        print_info("Building {}".format(self.build_options['project']))
        print_info("Running from {}".format(os.getcwd()))
        print_info("Project root is {}".format(self.project_root))

        # Platform agnostic defaults
        if 'defines' not in self.build_options:
            self.build_options['defines'] = []

        if 'cpp' not in self.build_options:
            self.build_options['cpp'] = True

        if 'arch' not in self.build_options:
            self.build_options['arch'] = 'x86_64'

        if 'binary_type' not in self.build_options:
            self.build_options['binary_type'] = 'executable'

        if 'disable_console' not in self.build_options:
            self.build_options['disable_console'] = False

        self.build_options['source_dir'] = os.path.realpath(self.build_options['source_dir'])

        
        # Platform specific build function
        if platform.system() == 'Windows':
            self.build_windows()
        elif platform.system() == 'Darwin':
            self.build_mac()
        elif platform.system() == 'Linux':
            self.build_linux()

    def build_linux(self):
        # Set up default options.
        if 'compiler' not in self.build_options['Linux']:
            if self.build_options['cpp']:
                self.build_options['Linux']['compiler'] = 'g++'
            else:
                self.build_options['Linux']['compiler'] = 'gcc'

        if 'system_libs' not in self.build_options['Linux']:
            self.build_options['Linux']['system_libs'] = []
        
        if 'user_libs' not in self.build_options['Linux']:
            self.build_options['Linux']['user_libs'] = []

        if 'extras' not in self.build_options['Linux']:
            self.build_options['Linux']['extras'] = []


            
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
            
        for extra in self.build_options['Linux']['extras']:
            self.push(extra)

        self.add_unix_source()
        self.add_unix_includes()
            
        self.push('-o ' + self.build_options['Linux']['out'])

        for lib in self.build_options['Linux']['user_libs']:
            self.push('-l' + lib)

        for lib in self.build_options['Linux']['system_libs']:
            self.push('-l' + lib)

        if self.build_options['binary_type'] == 'shared_library':
            self.push('-shared')
            self.push('-fPIC')

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

        if compile_error:
            print(colorama.Fore.RED + "[BUILD FAILED]" + colorama.Fore.RESET)
        else:
            print(colorama.Fore.GREEN + "[BUILD SUCCESSFUL]" + colorama.Fore.RESET)

        print('')

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

        if compile_error:
            print(colorama.Fore.RED + "[BUILD FAILED]")
        else:
            print(colorama.Fore.GREEN + "[BUILD SUCCESSFUL]")

        print('')

    def build_windows(self):
        win_options = self.build_options['Windows']
        self.push("cl.exe")

        for extra in self.build_options['Windows']['extras']:
            self.push(extra)

        # Tell the compiler whether to compile as C or C++
        if self.build_options['cpp']:
            self.push("/TP")
            self.push("/std:c++{}".format(self.build_options['cpp_standard']))
        else:
            self.push("/TC")

        # Output debug symbols
        if self.build_options['debug']:
            self.push("-Zi")

        # Disable warnings
        for warning in self.build_options['Windows']['warnings']:
            self.push("/wd{}".format(warning))

        # Specify runtime library
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

        if self.build_options['binary_type'] == BinaryType.SHARED_LIB:
            self.push('/LD')
                
        self.push("/link")
        for system_lib in self.build_options['Windows']['system_libs']:
            self.push(system_lib)

        for user_lib in self.build_options['Windows']['user_libs']:
            absolute_lib_dir = os.path.join(self.project_root, self.build_options['lib_dir'], user_lib)
            self.push(quote(absolute_lib_dir))

        if self.build_options['disable_console']:
            self.push('/SUBSYSTEM:windows')
            self.push('/ENTRY:mainCRTStartup')
        else:
            self.push('/SUBSYSTEM:console')
            
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

        if compile_error:
            print(colorama.Fore.RED + "[BUILD FAILED]" + colorama.Fore.RESET)
        else:
            print(colorama.Fore.GREEN + "[BUILD SUCCESSFUL]" + colorama.Fore.RESET)

        print('')
        
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
