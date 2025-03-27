import os
import importlib
import pkgutil
import sys
from pathlib import Path

def get_installed_version(package_name):
    try:
        return importlib.__import__(package_name).__version__
    except (ImportError, AttributeError):
        return None

def find_imports_in_directory(directory):
    imports = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        content = f.read()
                        for line in content.split('\n'):
                            line = line.strip()
                            if line.startswith('import ') or line.startswith('from '):
                                if ' import ' in line:
                                    package = line.split(' import ')[0].replace('from ', '')
                                    base_package = package.split('.')[0]
                                    imports.add(base_package)
                                else:
                                    package = line.replace('import ', '')
                                    if ',' in package:
                                        for p in package.split(','):
                                            imports.add(p.strip())
                                    else:
                                        base_package = package.split('.')[0]
                                        imports.add(base_package)
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
    return imports

def is_standard_library(module_name):
    return module_name in sys.builtin_module_names or module_name in {'os', 'sys', 'time', 'datetime', 're', 'json', 'math', 'random', 'collections', 'itertools', 'functools', 'typing', 'pathlib', 'uuid', 'hashlib', 'base64', 'logging', 'io', 'tempfile', 'shutil', 'csv', 'xml', 'html', 'urllib', 'http', 'socket', 'email', 'mimetypes', 'inspect', 'ast', 'importlib', 'pkgutil', 'traceback', 'contextlib', 'warnings', 'weakref', 'copy', 'enum', 'pickle', 'struct', 'calendar', 'operator', 'statistics', 'platform', 'string', 'argparse', 'configparser', 'textwrap', 'fnmatch', 'glob', 'zipfile', 'tarfile', 'gzip', 'bz2', 'lzma', 'zlib', 'threading', 'multiprocessing', 'subprocess', 'asyncio', 'concurrent', 'queue', 'sched', 'signal', 'shelve', 'dbm', 'sqlite3', 'xml', 'html', 'webbrowser', 'cgi', 'cgitb', 'wsgiref', 'urllib', 'http', 'ftplib', 'poplib', 'imaplib', 'nntplib', 'smtplib', 'smtpd', 'telnetlib', 'uuid', 'socketserver', 'xmlrpc', 'ipaddress', 'turtle', 'cmd', 'shlex', 'tkinter', 'curses', 'ctypes', 'distutils', 'ensurepip', 'venv', 'zipapp', 'abc', 'aifc', 'array', 'ast', 'asynchat', 'asyncore', 'audioop', 'binascii', 'builtins', 'cmath', 'code', 'codecs', 'codeop', 'colorsys', 'compileall', 'crypt', 'decimal', 'difflib', 'dis', 'doctest', 'errno', 'faulthandler', 'filecmp', 'fileinput', 'formatter', 'fractions', 'getopt', 'getpass', 'gettext', 'grp', 'heapq', 'hmac', 'imghdr', 'imp', 'keyword', 'linecache', 'locale', 'macpath', 'mailbox', 'mailcap', 'marshal', 'mmap', 'modulefinder', 'netrc', 'nis', 'numbers', 'ossaudiodev', 'parser', 'pdb', 'plistlib', 'poplib', 'posix', 'profile', 'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc', 'quopri', 'reprlib', 'resource', 'rlcompleter', 'runpy', 'sched', 'secrets', 'selectors', 'site', 'sndhdr', 'spwd', 'ssl', 'stat', 'stringprep', 'sunau', 'symbol', 'symtable', 'sysconfig', 'syslog', 'tabnanny', 'termios', 'test', 'timeit', 'token', 'tokenize', 'trace', 'tty', 'types', 'unicodedata', 'unittest', 'uu', 'venv', 'wave', 'winreg', 'winsound', 'wsgiref', 'xdrlib', 'zipimport'}

def main():
    app_dir = Path("app")
    if not app_dir.exists():
        print(f"Directory {app_dir} not found")
        return
    
    imports = find_imports_in_directory(app_dir)
    third_party_imports = [imp for imp in imports if not is_standard_library(imp)]
    
    # Get versions of installed packages
    requirements = []
    for package in sorted(third_party_imports):
        version = get_installed_version(package)
        if version:
            requirements.append(f"{package}=={version}")
        else:
            requirements.append(f"# {package} (version not found)")
    
    # Write to requirements.txt
    with open("requirements_auto.txt", "w") as f:
        f.write("# Auto-generated requirements\n")
        f.write("\n".join(requirements))
    
    print(f"Found {len(third_party_imports)} third-party imports.")
    print("Requirements written to requirements_auto.txt")

if __name__ == "__main__":
    main()
