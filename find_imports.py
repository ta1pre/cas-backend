import os
import re
import ast
from pathlib import Path

def extract_imports_from_file(file_path):
    """u30d5u30a1u30a4u30ebu304bu3089u5168u3066u306eu30a4u30f3u30ddu30fcu30c8u3092u62bdu51fau3059u308b"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # ASTu3092u4f7fu7528u3057u3066u30a4u30f3u30ddu30fcu30c8u3092u89e3u6790
        try:
            tree = ast.parse(content)
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.add(name.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
            
            return imports
        except SyntaxError:
            # u6b63u898fu8868u73feu3067u30a4u30f3u30ddu30fcu30c8u3092u62bdu51fauff08ASTu304cu5931u6557u3057u305fu5834u5408u306eu30d5u30a9u30fcu30ebu30d0u30c3u30afuff09
            import_pattern = re.compile(r'^\s*(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))', re.MULTILINE)
            matches = import_pattern.findall(content)
            imports = set()
            for match in matches:
                module = match[0] or match[1]
                imports.add(module.split('.')[0])
            return imports
    except Exception as e:
        print(f"u30a8u30e9u30fcuff08{file_path}uff09: {e}")
        return set()

def find_python_files(directory):
    """u6307u5b9au3055u308cu305fu30c7u30a3u30ecu30afu30c8u30eau5185u306eu5168u3066u306ePythonu30d5u30a1u30a4u30ebu3092u518du5e30u7684u306bu691cu7d22"""
    return list(Path(directory).rglob("*.py"))

def is_standard_library(module_name):
    """u30e2u30b8u30e5u30fcu30ebu304cu6a19u6e96u30e9u30a4u30d6u30e9u30eau304bu3069u3046u304bu3092u5224u5b9a"""
    import sys
    import importlib.util
    
    # u660eu3089u304bu306au6a19u6e96u30e9u30a4u30d6u30e9u30ea
    std_libs = {
        'abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections', 'configparser',
        'contextlib', 'copy', 'csv', 'datetime', 'decimal', 'difflib', 'enum', 'functools',
        'glob', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'importlib', 'inspect', 'io',
        'itertools', 'json', 'logging', 'math', 'multiprocessing', 'operator', 'os', 'pathlib',
        'pickle', 'platform', 'pprint', 'queue', 're', 'random', 'shutil', 'signal', 'socket',
        'sqlite3', 'statistics', 'string', 'struct', 'subprocess', 'sys', 'tempfile', 'threading',
        'time', 'traceback', 'types', 'typing', 'unittest', 'urllib', 'uuid', 'warnings', 'weakref',
        'xml', 'zipfile', 'zlib'
    }
    
    if module_name in std_libs:
        return True
    
    # u6a19u6e96u30e9u30a4u30d6u30e9u30eau306eu5834u6240u3092u78bau8a8d
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False
        
        # u6a19u6e96u30e9u30a4u30d6u30e9u30eau306fPythonu306eu30a4u30f3u30b9u30c8u30fcu30ebu30c7u30a3u30ecu30afu30c8u30eau306bu3042u308b
        return spec.origin is not None and 'site-packages' not in spec.origin
    except (ImportError, AttributeError):
        return False

def main():
    app_directory = "./app"
    all_imports = set()
    
    # Pythonu30d5u30a1u30a4u30ebu3092u691cu7d22
    python_files = find_python_files(app_directory)
    print(f"{len(python_files)}u500bu306ePythonu30d5u30a1u30a4u30ebu3092u691cu51fau3057u307eu3057u305f")
    
    # u5404u30d5u30a1u30a4u30ebu304bu3089u30a4u30f3u30ddu30fcu30c8u3092u62bdu51fa
    for file_path in python_files:
        imports = extract_imports_from_file(file_path)
        all_imports.update(imports)
    
    # u6a19u6e96u30e9u30a4u30d6u30e9u30eau3092u9664u5916
    third_party_imports = {module for module in all_imports if not is_standard_library(module)}
    
    # u7d50u679cu3092u8868u793a
    print("\n=== u30a2u30d7u30eau30b1u30fcu30b7u30e7u30f3u3067u4f7fu7528u3055u308cu3066u3044u308bu30b5u30fcu30c9u30d1u30fcu30c6u30a3u30e2u30b8u30e5u30fcu30eb ===")
    for module in sorted(third_party_imports):
        print(module)
    
    print(f"\nu5408u8a08: {len(third_party_imports)}u500bu306eu30b5u30fcu30c9u30d1u30fcu30c6u30a3u30e2u30b8u30e5u30fcu30ebu304cu898bu3064u304bu308au307eu3057u305f")

if __name__ == "__main__":
    main()
