import os, subprocess, sys, re, shutil, platform, colorama
from .utils import *
from .constants import BinaryType, BuildType
from .windows import build_windows


colorama.init()

# Base builder class. Reads in configurations, generates a compiler command, executes it. Provides
# 'virtual' methods you can override. 
class Builder():
    def __init__(self):
        self.build_options = None
        self.build_cmd = ""
        self.project_root = os.getcwd()

    def run(self):
        executable = os.path.join(os.getcwd(), self.build_options['build_dir'], self.build_options[platform.system()]['out'])
        subprocess.run([executable]) 
           
    def build(self):
        print_info("Building {}".format(self.build_options['project']))
        print_info("Running from {}".format(os.getcwd()))
        print_info("Project root is {}".format(self.project_root))

        self._add_platform_agnostic_defaults()
        
        # Platform specific build function
        if platform.system() == 'Windows':
            build_windows(self.build_options, self.project_root)
        elif platform.system() == 'Darwin':
            self.build_mac()
        elif platform.system() == 'Linux':
            self.build_linux()
            
    def get_output_filename(self):
        os_options = self.build_options[platform.system()]
        return os_options['out']
        
    def get_output_path(self):
        return os.path.realpath(os.path.join(self.build_options['build_dir'], self.get_output_filename()))

    def get_build_dir(self):
        return os.path.realpath(os.path.join(self.project_root, self.build_options['build_dir']))

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
            
        self._push(compiler_path)
        
        if self.build_options['cpp']:
            self._add_unix_cpp()
            
        if self.build_options['build_type'] == BuildType.DEBUG:
            self._push("-g")

        for define in self.build_options['defines']:
            self._push('-D {}'.format(define))
            
        for extra in self.build_options['Linux']['extras']:
            self._push(extra)

        self._add_unix_source()
        self._add_unix_includes()
            
        self._push('-o ' + self.build_options['Linux']['out'])

        for lib in self.build_options['Linux']['user_libs']:
            absolute_lib_path = os.path.join(self.project_root, self.build_options['lib_dir'], lib)
            absolute_lib_path = os.path.realpath(absolute_lib_path)
            self._push(absolute_lib_path)

        for lib in self.build_options['Linux']['system_libs']:
            self._push('-l' + lib)

        if self.build_options['binary_type'] == BinaryType.SHARED_LIB:
            self._push('-shared')
            self._push('-fPIC')

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
        # Defaults
        if 'compiler' not in self.build_options['Darwin']:
            if self.build_options['cpp']:
                self.build_options['Darwin']['compiler'] = 'clang++'
            else:
                self.build_options['Darwin']['compiler'] = 'clang'

        if 'extras' not in self.build_options['Darwin']:
            self.build_options['Darwin']['extras'] = {}

        if 'user_libs' not in self.build_options['Darwin']:
            self.build_options['Darwin']['user_libs'] = {}

        if 'system_libs' not in self.build_options['Darwin']:
            self.build_options['Darwin']['system_libs'] = {}

        if 'frameworks' not in self.build_options['Darwin']:
            self.build_options['Darwin']['frameworks'] = {}
            
        # Find the path to the compiler using 'which'
        compiler = self.build_options['Darwin']['compiler']
        process = subprocess.Popen(['which', compiler], stdout=subprocess.PIPE)
        compiler_path, err = process.communicate()
        compiler_path = compiler_path.decode('UTF-8').strip()
        if err or not compiler_path:
            print_error("tried to find your compiler using 'which {}', but it returned an error.".format(self.build_options['Darwin']['compiler']))
            exit()
            
        self._push(compiler_path)

        if self.build_options['build_type'] == BuildType.DEBUG:
            self._push("-g")

        for define in self.build_options['defines']:
            self._push('-D {}'.format(define))

        for extra in self.build_options['Darwin']['extras']:
            self._push(extra)
            
        if self.build_options['cpp']:
            self._add_unix_cpp()

        self._add_unix_source()
        self._add_unix_includes()

        if self.build_options['binary_type'] == BinaryType.SHARED_LIB:
            self._push('-dynamiclib')
            self._push('-fPIC')

        for lib in self.build_options['Darwin']['user_libs']:
            absolute_lib_path = os.path.join(self.project_root, self.build_options['lib_dir'], lib)
            absolute_lib_path = os.path.realpath(absolute_lib_path)
            self._push(absolute_lib_path)

        for lib in self.build_options['Darwin']['system_libs']:
            self._push('-l' + lib)

        for framework in self.build_options['Darwin']['frameworks']:
            self._push('-framework ' + framework)

        self._push('-o ' + self.build_options['Darwin']['out'])
        
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

    def _add_unix_source(self):
        for source in self.build_options['source_files']:
            absolute_source_file = os.path.join(self.project_root, self.build_options['source_dir'], source)
            absolute_source_file = os.path.realpath(absolute_source_file)
            self._push(absolute_source_file)
            
    def _add_unix_includes(self):
        for include in self.build_options['include_dirs']:
            absolute_include_dir = os.path.join(self.project_root, include)
            absolute_include_dir = os.path.realpath(absolute_include_dir)
            self._push("-I" + absolute_include_dir)
            
    def _add_unix_cpp(self):
        self._push("-std=c++{}".format(self.build_options['cpp_standard']))


    def _push(self, item):
        self.build_cmd = self.build_cmd + item + " "

    def _add_platform_agnostic_defaults(self):
        if 'defines' not in self.build_options:
            self.build_options['defines'] = []

        if 'cpp' not in self.build_options:
            self.build_options['cpp'] = True

        if 'arch' not in self.build_options:
            self.build_options['arch'] = 'x86_64'

        if 'binary_type' not in self.build_options:
            self.build_options['binary_type'] = BinaryType.EXECUTABLE

        if 'build_type' not in self.build_options:
            self.build_options['build_type'] = BuildType.DEBUG

        if 'disable_console' not in self.build_options:
            self.build_options['disable_console'] = False

        self.build_options['source_dir'] = os.path.realpath(self.build_options['source_dir'])
