import subprocess
with open("test_out2.txt", "w", encoding="utf-8") as f:
    subprocess.run([r".venv\Scripts\pytest", "tests/test_sdk.py", "-v", "--tb=short"], stdout=f, stderr=f)
