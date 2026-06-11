# Single-file-artifact pattern: the deliverable is one self-contained HTML file,
# but the source lives in src/ as numbered chunks concatenated in filename order.
# Tag boundaries (<style>, <script>) live in tiny .html shims so data/logic chunks
# are pure .css/.js. `make build` is byte-stable pure cat — no toolchain.
#   build  rebuild the artifact from src/
#   run    build, then serve on a free port (prints the URL)
#   check  artifact == cat(src/*) and no-loss invariant vs the certified baseline

PORT ?= 0
ARTIFACT := maintenance-api.html
BASELINE := versions/v98-pre-backtrail.html
SRC := $(sort $(wildcard src/*))

.PHONY: build run check

build: $(ARTIFACT)

$(ARTIFACT): $(SRC)
	cat $(SRC) > $@
	@echo "built $@ ($(words $(SRC)) chunks, $$(wc -c < $@ | tr -d ' ') bytes)"

define RUN_PY
import http.server
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", $(PORT)), http.server.SimpleHTTPRequestHandler)
print(f"Serving on http://127.0.0.1:{httpd.server_address[1]}/$(ARTIFACT)", flush=True)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print(" stopped.")
finally:
    httpd.server_close()
endef
export RUN_PY

run: build
	@python3 -c "$$RUN_PY"

define CHECK_PY
import re, sys
rebuilt = b"".join(open(p, "rb").read() for p in "$(SRC)".split())
if rebuilt != open("$(ARTIFACT)", "rb").read():
    sys.exit("DRIFT: $(ARTIFACT) != cat(src/*) — edit src/, then make build")
def inv(p):
    s = open(p, encoding="utf-8").read()
    return set(re.findall(r'href="([^"]+)"', s)), set(re.findall(r'\d[\d,.\-:]*', s))
h0, n0 = inv("$(BASELINE)")
h1, n1 = inv("$(ARTIFACT)")
gone_h, gone_n = sorted(h0 - h1), sorted(n0 - n1)
if gone_h or gone_n:
    sys.exit(f"NO-LOSS VIOLATION vs $(BASELINE)\n hrefs removed: {gone_h[:10]}\n tokens removed: {gone_n[:10]}")
print("check OK: artifact == cat(src/*); no-loss vs $(BASELINE) (0 href / 0 token removals)")
endef
export CHECK_PY

check:
	@python3 -c "$$CHECK_PY"
