import os, subprocess
from .constants import BinaryType, BuildType
from .utils import *

def build_windows(build_options, project_root):
    build_cmd = ''
    def push(item):
        nonlocal build_cmd
        build_cmd = build_cmd + item + " "

    win_options = build_options['Windows']
    push("cl.exe")

    for extra in build_options['Windows']['extras']:
        push(extra)

    # Tell the compiler whether to compile as C or C++
    if build_options['cpp']:
        push("/TP")
        push("/std:c++{}".format(build_options['cpp_standard']))
    else:
        push("/TC")

    # Output debug symbols
    if build_options['build_type'] == BuildType.DEBUG:
        push("-Zi")

    # Disable warnings
    for warning in build_options['Windows']['warnings']:
        push("/wd{}".format(warning))

    # Specify runtime library
    if win_options['runtime_library']:
        push("/" + build_options['Windows']['runtime_library'])

    for source_file in build_options['source_files']:
        absolute_source_file = os.path.join(project_root, build_options['source_dir'], source_file)
        push(quote(absolute_source_file))

    for include_dir in build_options['include_dirs']:
        absolute_include_dir = os.path.join(project_root, include_dir)
        push('/I{}'.format(quote(absolute_include_dir)))

    if 'defines' in build_options:
        for define in build_options['defines']:
            push('/D{}'.format(define))

    if build_options['binary_type'] == BinaryType.SHARED_LIB:
        push('/LD')
        
    push("/link")
    for system_lib in build_options['Windows']['system_libs']:
        push(system_lib)

    for user_lib in build_options['Windows']['user_libs']:
        absolute_lib_dir = os.path.join(project_root, build_options['lib_dir'], user_lib)
        push(quote(absolute_lib_dir))

    if build_options['disable_console']:
        push('/SUBSYSTEM:windows')
        push('/ENTRY:mainCRTStartup')
    else:
        push('/SUBSYSTEM:console')
        
    for ignore in build_options['Windows']['ignore']:
        push("/ignore:" + ignore)

    if 'arch' in build_options['Windows']:
        arch = build_options['Windows']['arch']
        if arch == 'x86_64':
            push("/MACHINE:X64")

    push("/out:" + build_options['Windows']['out'])

    make_cd_build_dir(build_options['build_dir'])

    # Copy DLLs
    if 'dlls' in build_options['Windows']:
        for dll in build_options['Windows']['dlls']:
            dll_path = os.path.join(project_root, build_options['lib_dir'], dll)
            shutil.copy(dll_path, os.getcwd())
            print_info("Copied DLL {} to {}".format(dll_path, os.getcwd()))
            
    print_info("Generated compiler command:")
    print_info(build_cmd)
    print_info("Invoking the compiler")
    
    # @hack: is there a better way to keep a process open?
    process = subprocess.Popen(build_cmd, stdout=subprocess.PIPE, env=os.environ.copy())
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
