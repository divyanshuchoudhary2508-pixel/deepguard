import sys
from pathlib import Path

# Ensure deepguard root is in sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.app import app

if __name__ == "__main__":
    print("=========================================================")
    print("  DeepGuard: Explainable Digital Image Verification Server")
    print("  Based on IEEE TENCON 2024 Research & Xception Model")
    print("=========================================================")
    print("Starting Flask web server on http://127.0.0.1:5000...")
    app.run(host="0.0.0.0", port=5000, debug=False)
