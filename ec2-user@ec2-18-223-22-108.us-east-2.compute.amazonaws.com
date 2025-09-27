from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Simple homepage with HTML + button
@app.route('/')
def index():
    html = """
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <title>Get IP Address</title>
      <style>
        body { font-family: system-ui, sans-serif; padding: 2rem; }
        button { padding: 10px 15px; font-size: 1rem; }
        pre { background: #f5f5f5; padding: 1rem; border-radius: 6px; }
      </style>
    </head>
    <body>
      <h1>Get Your IP Address</h1>
      <button onclick="getIP()">Show my IP</button>
      <pre id="output">—</pre>

      <script>
        async function getIP() {
          const res = await fetch("/get_ip");
          const data = await res.json();
          document.getElementById("output").textContent =
            "Your IP: " + data.ip;
        }
      </script>
    </body>
    </html>
    """
    return render_template_string(html)

# API endpoint to return the IP
@app.route('/get_ip')
def get_ip():
    # Try X-Forwarded-For first (useful if behind proxy/load balancer)
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return jsonify({"ip": ip})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)