import subprocess
import sys
import os

def main():
    if not os.path.exists("app.py"):
        print("app.py not found")
        return

    try:
        import streamlit  
    except ImportError:
        print("Installing streamlit...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])

    print("Starting Freshservice Assistant...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    main()
