#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def create_corrected_views():
    try:
        # Read the original file
        with open('home/views.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Replace all problematic strftime formats
        # %p is not valid in Python strftime, we'll use a custom approach for AM/PM
        old_format = '%B %d, %Y at %I:%M %p'
        new_format = '%B %d, %Y at %I:%M %p'
        
        # Replace all occurrences
        content = content.replace(old_format, new_format)
        
        # Also fix any broken lines with line breaks in the middle
        content = content.replace('%B %d, %Y at %I:%M\n%p', '%B %d, %Y at %I:%M %p')
        content = content.replace('%B %d, %Y at %I:%M \n%p', '%B %d, %Y at %I:%M %p')
        
        # Write to a new file
        with open('home/views_corrected.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Created corrected views.py file")
        
        # Test syntax of the corrected file
        import ast
        try:
            ast.parse(content)
            print("Syntax check passed!")
        except SyntaxError as e:
            print(f"Syntax error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_corrected_views()
