# Python Dependency Scanner

This tool scans Python projects for imports, generates a `requirements.txt` file, and sets up a virtual environment with the required packages. It's especially useful for projects where import names differ from package names.

## Features

- Scans Python files for import statements
- Handles cases where import names differ from package names
- Generates a `requirements.txt` file
- Creates or uses an existing virtual environment
- Installs required packages in the virtual environment

## Usage

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/python-dependency-scanner.git
   cd python-dependency-scanner
   ```

2. Install the required package:
   ```
   pip install chardet
   ```

3. Run the script:
   ```
   python dependency_scanner.py
   ```

4. Follow the prompts to complete the installation process.

## Customizing Package Mapping

The script uses a `package_mapping.json` file to handle cases where import names differ from package names. You can add more mappings to this file as needed:

1. Open `package_mapping.json`
2. Add new entries in the format: `"import_name": "package_name"`
3. Save the file

The script will automatically use your updated mappings the next time it runs.

## Contributing

Contributions are welcome! Feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
