from cx_Freeze import setup, Executable

base = None

executables = [Executable("yoni.py", base=base)]

packages = ["idna", 'numpy', 'pandas', 'jinja2', 'matplotlib', 'glob', 'warnings',
            'os', 'scipy', 'scikit_posthocs', 'datetime', 'seaborn', 'pickle', 'copy']
options = {
    'build_exe': {
        'packages': packages,
        "excludes": ['scipy.spatial.cKDTree']
    },
}

setup(
    name="yoni2.0",
    options=options,
    version="1",
    description='yoni2.0',
    executables=executables
)