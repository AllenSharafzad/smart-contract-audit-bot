#!/usr/bin/env python3
"""
Clear Python cache files
"""
import os
import shutil

def clear_pycache(directory="."):
    """Remove all __pycache__ directories and .pyc files"""
    for root, dirs, files in os.walk(directory):
        # Remove __pycache__ directories
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            print(f"Removing: {pycache_path}")
            shutil.rmtree(pycache_path)
            dirs.remove("__pycache__")
        
        # Remove .pyc files
        for file in files:
            if file.endswith(".pyc"):
                pyc_path = os.path.join(root, file)
                print(f"Removing: {pyc_path}")
                os.remove(pyc_path)

if __name__ == "__main__":
    clear_pycache()
    print("Cache cleared!")