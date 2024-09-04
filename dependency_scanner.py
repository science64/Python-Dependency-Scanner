import os
import ast
import subprocess
import sys
import chardet
import importlib.metadata
import warnings
import json

# Suppress DeprecationWarning for pkg_resources
warnings.filterwarnings("ignore", category=DeprecationWarning)

def load_package_mapping():
    """Load the package mapping from JSON file."""
    try:
        with open('package_mapping.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: package_mapping.json not found. Using empty mapping.")
        return {}

PACKAGE_MAPPING = load_package_mapping()

def is_external_package(module_name):
    """Check if a module is an external package."""
    try:
        importlib.metadata.distribution(module_name)
        return True
    except importlib.metadata.PackageNotFoundError:
        # Check if it's a known package with a different import name
        if module_name in PACKAGE_MAPPING:
            try:
                importlib.metadata.distribution(PACKAGE_MAPPING[module_name])
                return True
            except importlib.metadata.PackageNotFoundError:
                pass
        return False

def get_package_name(module_name):
    """Get the correct package name for a given module name."""
    return PACKAGE_MAPPING.get(module_name, module_name)

def scan_imports(file_path):
    try:
        with open(file_path, 'rb') as file:
            raw_content = file.read()
            encoding = chardet.detect(raw_content)['encoding']
        
        with open(file_path, 'r', encoding=encoding) as file:
            tree = ast.parse(file.read())
        
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    if is_external_package(module_name):
                        imports.add(get_package_name(module_name))
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0:  # absolute import
                    module_name = node.module.split('.')[0]
                    if is_external_package(module_name):
                        imports.add(get_package_name(module_name))
        
        return imports
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        return set()

def scan_directory(directory):
    all_imports = set()
    for root, _, files in os.walk(directory):
        if '.venv' in root.split(os.path.sep):
            continue  # Skip .venv directory
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                all_imports.update(scan_imports(file_path))
    
    return all_imports

def create_requirements_file(imports, filename='requirements.txt'):
    with open(filename, 'w') as f:
        for imp in sorted(imports):
            f.write(f"{imp}\n")

def find_existing_venv():
    venv_names = ['.venv', 'venv', 'myenv']
    for venv in venv_names:
        if os.path.isdir(venv):
            return venv
    return None

def create_or_use_venv():
    existing_venv = find_existing_venv()
    if existing_venv:
        print(f"Using existing virtual environment: {existing_venv}")
        return existing_venv
    else:
        venv_name = '.venv'
        print(f"Creating new virtual environment: {venv_name}")
        subprocess.run([sys.executable, '-m', 'venv', venv_name], check=True)
        return venv_name

def upgrade_pip(venv_name):
    if os.name == 'nt':  # Windows
        python_path = os.path.join(venv_name, 'Scripts', 'python')
    else:  # macOS and Linux
        python_path = os.path.join(venv_name, 'bin', 'python')
    
    print("Upgrading pip...")
    try:
        subprocess.run([python_path, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
    except subprocess.CalledProcessError:
        print("Failed to upgrade pip. Continuing with installation...")

def install_requirements(venv_name, requirements_file):
    if os.name == 'nt':  # Windows
        pip_path = os.path.join(venv_name, 'Scripts', 'pip')
    else:  # macOS and Linux
        pip_path = os.path.join(venv_name, 'bin', 'pip')
    
    with open(requirements_file, 'r') as f:
        modules = f.read().splitlines()
    
    print("The following modules will be installed:")
    for module in modules:
        print(f"- {module}")
    
    user_input = input("Do you want to proceed with the installation? (yes/no): ").lower()
    if user_input != 'yes':
        print("Installation cancelled.")
        return
    
    print(f"Installing dependencies in '{venv_name}'...")
    subprocess.run([pip_path, 'install', '-r', requirements_file], check=True)

def main():
    directory = os.getcwd()  # Use current directory
    print(f"Scanning directory: {directory}")
    
    print("Scanning for imports...")
    imports = scan_directory(directory)
    
    print("Creating requirements.txt...")
    create_requirements_file(imports)
    
    venv_name = create_or_use_venv()
    
    upgrade_pip(venv_name)
    
    install_requirements(venv_name, 'requirements.txt')
    
    print("Done! Your virtual environment is ready.")

if __name__ == "__main__":
    main()