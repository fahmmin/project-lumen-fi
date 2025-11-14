"""
PROJECT LUMEN - Setup Verification Script
Run this to verify your installation is correct
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.9+)")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'sentence_transformers',
        'faiss',
        'transformers',
        'torch',
        'sklearn',
        'PIL',
        'pdfminer',
        'pytesseract',
        'rank_bm25'
    ]

    all_ok = True
    for package in required_packages:
        try:
            if package == 'pdfminer':
                __import__('pdfminer.six')
            elif package == 'sklearn':
                __import__('sklearn')
            elif package == 'PIL':
                __import__('PIL')
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (MISSING)")
            all_ok = False

    return all_ok

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    print("\nChecking Tesseract OCR...")
    try:
        result = subprocess.run(['tesseract', '--version'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ Tesseract found: {version_line}")
            return True
        else:
            print("❌ Tesseract not properly installed")
            return False
    except FileNotFoundError:
        print("❌ Tesseract not found in PATH")
        print("   Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    except Exception as e:
        print(f"❌ Error checking Tesseract: {e}")
        return False

def check_env_file():
    """Check if .env file exists"""
    print("\nChecking configuration...")
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file found")
        return True
    else:
        print("⚠️  .env file not found")
        print("   Copy .env.example to .env and configure it")
        return False

def check_directory_structure():
    """Check if all required directories exist"""
    print("\nChecking directory structure...")
    required_dirs = [
        'backend',
        'backend/routers',
        'backend/rag',
        'backend/agents',
        'backend/utils',
        'backend/data',
        'backend/data/policy_docs',
        'frontend'
    ]

    all_ok = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} (MISSING)")
            all_ok = False

    return all_ok

def check_key_files():
    """Check if key files exist"""
    print("\nChecking key files...")
    required_files = [
        'backend/main.py',
        'backend/config.py',
        'requirements.txt',
        'frontend/index.html',
        'frontend/app.js',
        'frontend/styles.css',
        'README.md'
    ]

    all_ok = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (MISSING)")
            all_ok = False

    return all_ok

def test_imports():
    """Test key imports"""
    print("\nTesting key imports...")

    tests = [
        ("FastAPI", "from fastapi import FastAPI"),
        ("Sentence Transformers", "from sentence_transformers import SentenceTransformer"),
        ("FAISS", "import faiss"),
        ("PyTorch", "import torch"),
        ("Transformers", "from transformers import T5Tokenizer"),
        ("scikit-learn", "from sklearn.ensemble import IsolationForest"),
    ]

    all_ok = True
    for name, import_str in tests:
        try:
            exec(import_str)
            print(f"✅ {name}")
        except Exception as e:
            print(f"❌ {name}: {str(e)[:50]}")
            all_ok = False

    return all_ok

def main():
    print_header("PROJECT LUMEN - Setup Verification")

    results = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Tesseract OCR": check_tesseract(),
        "Configuration": check_env_file(),
        "Directory Structure": check_directory_structure(),
        "Key Files": check_key_files(),
        "Import Tests": test_imports()
    }

    print_header("VERIFICATION SUMMARY")

    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check:.<40} {status}")

    print("\n" + "="*60)

    if all(results.values()):
        print("\n🎉 ALL CHECKS PASSED!")
        print("\nYour PROJECT LUMEN installation is ready to use.")
        print("\nNext steps:")
        print("  1. Configure your .env file (especially OPENAI_API_KEY)")
        print("  2. Run: python backend/main.py")
        print("  3. Open: http://localhost:8000/docs")
        print("  4. Or use quick start scripts: run.bat (Windows) or ./run.sh (Mac/Linux)")
    else:
        print("\n⚠️  SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running PROJECT LUMEN.")
        print("\nFor help, see:")
        print("  - QUICKSTART.md for setup instructions")
        print("  - README.md for detailed documentation")
        print("  - requirements.txt for dependency list")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
