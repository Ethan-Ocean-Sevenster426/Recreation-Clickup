#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def fix_views_file():
    try:
        # Read the file with error handling
        with open('home/views.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Write the cleaned content back
        with open('home/views.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("File has been cleaned and rewritten.")
        
        # Test if the syntax is now valid
        import ast
        try:
            ast.parse(content)
            print("Syntax check passed!")
        except SyntaxError as e:
            print(f"Syntax error still exists: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_views_file()
