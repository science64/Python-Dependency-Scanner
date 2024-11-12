import os
import ast
import subprocess
import sys
import chardet
import importlib.metadata
import warnings
import json
import argparse

# Suppress DeprecationWarning for pkg_resources
warnings.filterwarnings("ignore", category=DeprecationWarning)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Scan Python files for imports and create a virtual environment with required packages.'
    )
    parser.add_argument(
        '-i', '--input-dir',
        help='Directory containing Python files to scan (default: current directory)',
        default=None
    )
    return parser.parse_args()

def get_directory_input():
    """Get directory path from user input and validate it."""
    while True:
        directory = input("Enter the directory to scan (press Enter for current directory): ").strip()
        if not directory:
            return os.getcwd()
        if os.path.isdir(directory):
            return os.path.abspath(directory)
        print(f"Error: '{directory}' is not a valid directory. Please try again.")

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
    # Common standard library modules to exclude
    stdlib_modules = set([
        'os', 'sys', 'datetime', 'math', 'random', 'time', 'json', 
        'csv', 're', 'collections', 'itertools', 'functools', 'typing',
        'pathlib', 'logging', 'argparse', 'unittest', 'warnings'
    ])
    
    # If it's a standard library module, it's not external
    if module_name in stdlib_modules:
        return False
        
    # First check if it's in our mapping
    if module_name in PACKAGE_MAPPING:
        try:
            importlib.metadata.distribution(PACKAGE_MAPPING[module_name])
            print(f"Found {module_name} in package mapping as {PACKAGE_MAPPING[module_name]}")
            return True
        except importlib.metadata.PackageNotFoundError:
            print(f"Note: {module_name} is in mapping but {PACKAGE_MAPPING[module_name]} is not installed")
            return True  # Still return True as it's a known external package
    
    # Then try the module name directly
    try:
        importlib.metadata.distribution(module_name)
        print(f"Found {module_name} as installed package")
        return True
    except importlib.metadata.PackageNotFoundError:
        # Additional check for common external packages that might not be installed
        common_external = {
            'cv2', 'mediapipe', 'tensorflow', 'torch', 'pandas', 'numpy', 
            'scipy', 'matplotlib', 'seaborn', 'sklearn', 'PIL'
        }
        if module_name in common_external:
            print(f"Recognized {module_name} as common external package")
            return True
            
        print(f"Note: {module_name} not found as installed package")
        return False

def get_package_name(module_name):
    """Get the correct package name for a given module name."""
    return PACKAGE_MAPPING.get(module_name, module_name)

def scan_imports(file_path):
    try:
        # Read file content with detailed error handling
        try:
            with open(file_path, 'rb') as file:
                raw_content = file.read()
                detected = chardet.detect(raw_content)
                encoding = detected['encoding']
                if not encoding:
                    print(f"Warning: Could not detect encoding for {file_path}, falling back to utf-8")
                    encoding = 'utf-8'
                print(f"Processing {file_path} with detected encoding: {encoding}")
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return set()

        # Parse file content with detailed error handling
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
                tree = ast.parse(content)
        except Exception as e:
            print(f"Error parsing Python syntax in {file_path}: {str(e)}")
            return set()

        imports = set()
        for node in ast.walk(tree):
            try:
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split('.')[0]
                        print(f"Found import in {file_path}: {module_name}")
                        if is_external_package(module_name):
                            imports.add(get_package_name(module_name))
                        else:
                            print(f"Note: {module_name} not identified as external package")
                elif isinstance(node, ast.ImportFrom):
                    if node.level == 0:  # absolute import
                        module_name = node.module.split('.')[0]
                        print(f"Found from-import in {file_path}: {module_name}")
                        if is_external_package(module_name):
                            imports.add(get_package_name(module_name))
                        else:
                            print(f"Note: {module_name} not identified as external package")
            except Exception as e:
                print(f"Error processing import node in {file_path}: {str(e)}")
                continue
        
        return imports
    except Exception as e:
        print(f"Unexpected error processing file {file_path}: {str(e)}")
        return set()

def scan_directory(directory):
    all_imports = set()
    for root, _, files in os.walk(directory):
        if '.venv' in root.split(os.path.sep):
            continue  # Skip .venv directory
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                file_imports = scan_imports(file_path)
                all_imports.update(file_imports)
                if file_imports:
                    print(f"Found imports in {file_path}: {', '.join(file_imports)}")
    
    return all_imports

def create_requirements_file(imports, project_dir, filename='requirements.txt'):
    filepath = os.path.join(project_dir, filename)
    with open(filepath, 'w') as f:
        for imp in sorted(imports):
            f.write(f"{imp}\n")
    return filepath

def find_existing_venv(directory):
    venv_names = ['.venv', 'venv', 'myenv']
    for venv in venv_names:
        venv_path = os.path.join(directory, venv)
        if os.path.isdir(venv_path):
            return venv_path
    return None

def create_or_use_venv(directory):
    existing_venv = find_existing_venv(directory)
    if existing_venv:
        print(f"Using existing virtual environment: {existing_venv}")
        return os.path.basename(existing_venv)
    else:
        venv_name = '.venv'
        venv_path = os.path.join(directory, venv_name)
        print(f"Creating new virtual environment: {venv_path}")
        subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
        return venv_name

def upgrade_pip(venv_dir):
    if os.name == 'nt':  # Windows
        python_path = os.path.join(venv_dir, 'Scripts', 'python')
    else:  # macOS and Linux
        python_path = os.path.join(venv_dir, 'bin', 'python')
    
    print("Upgrading pip...")
    try:
        subprocess.run([python_path, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
    except subprocess.CalledProcessError:
        print("Failed to upgrade pip. Continuing with installation...")

def install_requirements(venv_dir, requirements_file):
    if os.name == 'nt':  # Windows
        pip_path = os.path.join(venv_dir, 'Scripts', 'pip')
    else:  # macOS and Linux
        pip_path = os.path.join(venv_dir, 'bin', 'pip')
    
    with open(requirements_file, 'r') as f:
        modules = f.read().splitlines()
    
    print("\nThe following modules will be installed:")
    for module in modules:
        print(f"- {module}")
    
    user_input = input("\nDo you want to proceed with the installation? (yes/no): ").lower()
    if user_input != 'yes':
        print("Installation cancelled.")
        return
    
    print(f"\nInstalling dependencies in '{venv_dir}'...")
    subprocess.run([pip_path, 'install', '-r', requirements_file], check=True)

def main():
    args = parse_arguments()
    
    # Get and validate project directory
    if args.input_dir:
        project_dir = os.path.abspath(args.input_dir)
        if not os.path.isdir(project_dir):
            print(f"Error: Directory '{project_dir}' does not exist.")
            sys.exit(1)
    else:
        project_dir = get_directory_input()
    
    print(f"\nScanning directory: {project_dir}")
    
    print("\nScanning for imports...")
    imports = scan_directory(project_dir)
    
    if not imports:
        print("\nNo external package imports found.")
        sys.exit(0)
    
    print("\nCreating requirements.txt...")
    requirements_file = create_requirements_file(imports, project_dir)
    print(f"Requirements file created at: {requirements_file}")
    
    venv_name = create_or_use_venv(project_dir)
    venv_path = os.path.join(project_dir, venv_name)
    
    upgrade_pip(venv_path)
    
    install_requirements(venv_path, requirements_file)
    
    print("\nDone! Your virtual environment is ready.")
    print(f"Virtual environment location: {venv_path}")
    print(f"Requirements file location: {requirements_file}")

if __name__ == "__main__":
    main()