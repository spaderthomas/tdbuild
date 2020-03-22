import tdbuild.tdbuild as tdbuild

build_options = {
    'source_dir': '.',
    'build_dir': 'build',
    'source_files': [
        'main.c'
    ],
    'include_dirs': [],
    'lib_dir': '',
    'debug': True,
    'cpp': False,
    'cpp_standard': '17',
    'Windows': {
        'system_libs': [],
        'user_libs': [],
        'dlls': [],
        'ignore': [],
        'machine': '',
        'out': '',
        'runtime_library': '',
        'warnings': [],
        'extras': []
    },
    'Darwin': {
        'compiler': '',
        'user_libs': [],
        'system_libs': [],
        'frameworks': [],
        'out': '',
        'extras': []
    },
    'Linux': {
        'compiler': 'gcc',
        'user_libs': [],
        'system_libs':[],
        'extras': [],
        'out': 'hello'
    }
}

class Builder(tdbuild.base_builder):
    def __init__(self):
        super().__init__()

    def build(self):
        super().build()
        
    def run(self):
        super().run()
        
    def setup(self):
        super().setup()
        
    def prebuild(self):
        pass
    
