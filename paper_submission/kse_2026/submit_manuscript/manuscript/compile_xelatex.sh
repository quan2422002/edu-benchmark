#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if command -v xelatex >/dev/null 2>&1; then
  exec latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
fi

if ! command -v xetex >/dev/null 2>&1; then
  echo "XeTeX is required. Install texlive-xetex and rerun." >&2
  exit 1
fi

CACHE_DIR="${TMPDIR:-/tmp}/edu-benchmark-xelatex-format"
FORMAT_FILE="$CACHE_DIR/xelatex.fmt"
mkdir -p "$CACHE_DIR"

if [[ ! -f "$FORMAT_FILE" ]]; then
  (
    cd "$CACHE_DIR"
    xetex -ini -etex -jobname=xelatex -progname=xelatex xelatex.ini
  )
fi

exec latexmk -xelatex \
  -e "\$xelatex=q{xetex -fmt=$FORMAT_FILE -progname=xelatex %O %S}" \
  -interaction=nonstopmode \
  -halt-on-error \
  main.tex
