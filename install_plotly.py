"""
Install Plotly and Kaleido for professional PDF report visualizations

This script installs the required packages for generating
high-quality Gantt charts using Plotly instead of matplotlib.

Benefits of Plotly:
- Professional, publication-quality charts
- No overlapping text or alignment issues
- Clean, modern design
- Perfect rendering every time
- Used by Fortune 500 companies
"""
import subprocess
import sys

def install_packages():
    """Install Plotly and required dependencies"""

    print("="*70)
    print("INSTALLING PLOTLY FOR PROFESSIONAL GANTT CHARTS")
    print("="*70)
    print()

    packages = [
        ('plotly', 'Core plotting library'),
        ('kaleido', 'Static image export (for PDF generation)'),
        ('pandas', 'Data manipulation (required by Plotly)')
    ]

    print("Packages to install:")
    for pkg, desc in packages:
        print(f"  - {pkg}: {desc}")
    print()

    try:
        for pkg, desc in packages:
            print(f"Installing {pkg}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])
            print(f"[OK] {pkg} installed successfully!")
            print()

        print("="*70)
        print("SUCCESS! All packages installed")
        print("="*70)
        print()
        print("Your PDF reports will now use professional Plotly charts!")
        print("Run python test_send_report_email.py to test the new charts")
        print()

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Installation failed: {e}")
        print()
        print("Please try installing manually:")
        print("  pip install plotly kaleido pandas")
        return False

    return True

if __name__ == '__main__':
    success = install_packages()
    sys.exit(0 if success else 1)
