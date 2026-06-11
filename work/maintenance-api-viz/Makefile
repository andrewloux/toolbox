PORT ?= 0

define RUN_PY
import http.server
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", $(PORT)), http.server.SimpleHTTPRequestHandler)
print(f"Serving on http://127.0.0.1:{httpd.server_address[1]}/maintenance-api.html", flush=True)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print(" stopped.")
finally:
    httpd.server_close()
endef
export RUN_PY

.PHONY: run
run:
	@python3 -c "$$RUN_PY"
