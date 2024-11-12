# Python Dependency Scanner

A smart Python tool that automatically scans your Python projects, detects imports, generates requirements.txt, and sets up a virtual environment. It's especially useful for handling imports where package names differ from import names (like `cv2` → `opencv-python`).

## Key Features

- 🔍 **Smart Import Detection**: Recognizes common packages like `cv2`, `mediapipe`, `tensorflow` even if not installed
- 🗺️ **Import Name Mapping**: Handles cases where import names differ from package names
- 📝 **Requirements Generation**: Creates `requirements.txt` in your project directory
- 🔧 **Virtual Environment**: Automatically creates/reuses virtual environment
- 📦 **Package Installation**: Installs all required packages with confirmation
- 🔄 **Encoding Support**: Automatically handles different file encodings

## Quick Start

<<<<<<< HEAD
```bash
# Install required package
pip install chardet
=======
1. Clone this repository:
   ```
   git clone https://github.com/science64/python-dependency-scanner.git
   cd python-dependency-scanner
   ```
>>>>>>> 3329e18af5f40ec4417e128df09c09079989b46d

# Run the scanner (interactive mode)
python dependency_scanner.py

# Or specify directory directly
python dependency_scanner.py -i /path/to/your/project
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/science64/python-dependency-scanner.git
cd python-dependency-scanner
```

2. Install required package:
```bash
pip install chardet
```

## Usage Examples

### Basic Usage
```bash
# Scan current directory
python dependency_scanner.py

# Scan specific project
python dependency_scanner.py -i /path/to/project
```

### What It Does

When you run the scanner, it will:
1. Recursively scan all Python files in the directory
2. Detect imports like:
   - Standard imports (`import numpy`)
   - Aliased imports (`import pandas as pd`)
   - From imports (`from PIL import Image`)
3. Create requirements.txt
4. Set up virtual environment
5. Install packages after confirmation

### Example Output

```
Scanning directory: /path/to/project

Found imports in main.py: 
- opencv-python (from import cv2)
- mediapipe
- numpy
- python-dotenv

Creating requirements.txt...
Requirements file created at: /path/to/project/requirements.txt

Creating new virtual environment: .venv
The following modules will be installed:
- opencv-python
- mediapipe
- numpy
- python-dotenv

Do you want to proceed with the installation? (yes/no):
```

## Smart Package Detection

The scanner recognizes packages in three ways:
1. 📗 Through the package mapping file
2. 🔍 By checking installed packages
3. 📦 Through a built-in list of common packages

### Built-in Package Recognition
Common packages that are automatically recognized include:
- `cv2` (opencv-python)
- `mediapipe`
- `tensorflow`
- `torch`
- `pandas`
- `numpy`
- `PIL`
- And more...

## Package Name Mapping

The tool includes a `package_mapping.json` file that maps import names to package names. For example:
```json
{
    "PIL": "Pillow",
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
    "bs4": "beautifulsoup4"
}
```

### Adding Custom Mappings

You can add your own mappings:
1. Open `package_mapping.json`
2. Add new entries:
   ```json
   {
       "your_import": "package-name"
   }
   ```

## Project Structure

After running the scanner, your project will look like this:
```
your-project/
├── .venv/                  # Virtual environment
├── requirements.txt        # Generated requirements
├── your_python_files.py
└── ...
```

## Debugging

If certain imports aren't being detected:
1. Run with `-i` flag to specify directory explicitly
2. Check if the Python file has proper `.py` extension
3. Verify file permissions
4. Ensure the file isn't in an excluded directory (like `.venv`)

## Contributing

Contributions are welcome! Areas for improvement:
- Additional package mappings
- Support for more virtual environment configurations
- Enhanced import detection patterns
- Performance optimizations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the `chardet` library for encoding detection
- All contributors to the package mapping database
- Python community for package naming standards