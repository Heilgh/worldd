#!/usr/bin/env python3
import subprocess
import sys
import os

def install_dev():
    """Install the package in development mode"""
    try:
        # Install dependencies
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        # Install package in development mode
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        
        print("Development installation successful!")
        print("You can now run the game with: python -m src.main")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during installation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_dev() 