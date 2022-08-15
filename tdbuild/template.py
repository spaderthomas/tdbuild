import tdbuild

build_options = {
    'project': '',
    'source_dir': '',
    'include_dirs': [],
    'lib_dir': '',
    'build_dir': '',
    'source_files': [],
    'debug': True,
    'cpp': True,
    'cpp_standard': '17',
	'defines': [],
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
        'compiler': '',
        'user_libs': [],
        'system_libs':[],
        'extras': [],
        'out': ''
    }
}

class Builder(tdbuild.Builder):
    def __init__(self):
        super().__init__()

    def build(self):
        super().build()
        
    def run(self):
        super().run()
