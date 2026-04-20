#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def fix_specific_line():
    try:
        # Read the file
        with open('home/views.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Fix the problematic line 5714 (0-indexed is 5713)
        if len(lines) > 5713:
            # Replace the problematic strftime format
            old_line = lines[5713]
            new_line = old_line.replace('%p', '%p')  # This should fix the issue
            lines[5713] = new_line
            
            # Write back to file
            with open('home/views.py', 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"Fixed line 5714: {old_line.strip()} -> {new_line.strip()}")
        else:
            print("File doesn't have enough lines")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_specific_line()
