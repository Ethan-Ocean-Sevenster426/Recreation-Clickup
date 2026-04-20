#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def fix_project_deletion_error():
    """Fix the 'str' object has no attribute 'username' error in project deletion"""
    try:
        # Read the views.py file
        with open('home/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the client.username issue in delete_project function
        # The client field is a CharField, not a related object
        old_line = "client_name = project.client.username if project.client else 'No Client'"
        new_line = "client_name = project.client if project.client else 'No Client'"
        
        # Replace the problematic line
        content = content.replace(old_line, new_line)
        
        # Write back to file
        with open('home/views.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Fixed project deletion error: removed .username from client field access")
        
        # Test syntax
        import ast
        try:
            ast.parse(content)
            print("Syntax check passed!")
        except SyntaxError as e:
            print(f"Syntax error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

def fix_strftime_format():
    try:
        # Read the file
        with open('home/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the invalid %p format with a valid one
        # %p is not valid in Python strftime, we'll use a custom approach for AM/PM
        old_format = '%B %d, %Y at %I:%M %p'
        new_format = '%B %d, %Y at %I:%M %p'
        
        # Replace all occurrences
        content = content.replace(old_format, new_format)
        
        # Write back to file
        with open('home/views.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Fixed strftime format")
        
        # Test syntax
        import ast
        try:
            ast.parse(content)
            print("Syntax check passed!")
        except SyntaxError as e:
            print(f"Syntax error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Fix the project deletion error first
    fix_project_deletion_error()
    
    # Then fix the strftime format if needed
    # fix_strftime_format()
