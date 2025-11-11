"""
Launch the MR Frequency Sculptor GUI application.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.gui import MRFrequencySculptorApp
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MRFrequencySculptorApp()
    window.showFullScreen()
    
    sys.exit(app.exec_())

