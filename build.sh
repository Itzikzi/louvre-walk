#!/bin/sh
# Wraps louvre.html (the claude.ai Artifact source) into index.html for GitHub Pages:
# adds the document head, app manifest and service-worker registration.
# Run after editing louvre.html, and bump VERSION in sw.js.
set -e
cd "$(dirname "$0")"
{
  printf '%s\n' '<!doctype html>' '<html lang="he" dir="rtl">' '<head>' \
    '<meta charset="utf-8">' '<meta name="robots" content="noindex">' \
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">' \
    '<link rel="manifest" href="manifest.webmanifest">' \
    '<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">' \
    '<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>' \
    '</head>' '<body>'
  cat louvre.html
  printf '%s\n' "<script>if('serviceWorker' in navigator)navigator.serviceWorker.register('sw.js').catch(function(){});</script>" '</body>' '</html>'
} > index.html
echo "built index.html"
