#!/bin/bash
# Fails (exit 1) if anything private is tracked or committable.
# "Committable" = git ls-files plus git ls-files --others --exclude-standard (untracked and not ignored).
# Run by .git/hooks/pre-commit; run it by hand before any push.
cd "$(dirname "$0")/.." || exit 2
fail=0
list=$( (git ls-files; git ls-files --others --exclude-standard) | sort -u)

# 1. file names that must never be committable. The one allowed exception is the harmless loader assets/private_loader.js.
bad=$(printf '%s\n' "$list" | grep -v '^assets/private_loader\.js$' | grep -E '(^|/)private_|data/private|jhu_|statista_|LOGBOOK|\.pre_|data/raw|^data/sources_manifest\.csv$|\.pid$|\.local_server')
if [ -n "$bad" ]; then
  echo "FAIL: private file names are tracked or committable:"; printf '%s\n' "$bad" | sed 's/^/  /'; fail=1
fi

# 2. content that must never appear in a committable file (case-insensitive; this script is skipped because it names the patterns)
files=$(printf '%s\n' "$list" | grep -v '^scripts/check_public\.sh$' | while IFS= read -r f; do [ -f "$f" ] && printf '%s\n' "$f"; done)
hits=$(printf '%s\n' "$files" | tr '\n' '\0' | xargs -0 grep -I -i -l -F -e 'proquest.com/docview' -e 'pitchbook.com' -e 'ezproxy' -e '/Users/' 2>/dev/null)
hits2=$(printf '%s\n' "$files" | tr '\n' '\0' | xargs -0 grep -I -i -l -E '[A-Za-z0-9._%+-]+@jh\.edu' 2>/dev/null)
all=$(printf '%s\n%s\n' "$hits" "$hits2" | sed '/^$/d' | sort -u)
if [ -n "$all" ]; then
  echo "FAIL: forbidden content (proquest.com/docview, pitchbook.com, ezproxy, /Users/, @jh.edu) in committable files:"
  for f in $all; do
    for p in 'proquest.com/docview' 'pitchbook.com' 'ezproxy' '/Users/'; do
      n=$(grep -I -i -c -F -e "$p" "$f" 2>/dev/null); [ "${n:-0}" -gt 0 ] && echo "  $f  [$p x$n]"
    done
    n=$(grep -I -i -c -E '[A-Za-z0-9._%+-]+@jh\.edu' "$f" 2>/dev/null); [ "${n:-0}" -gt 0 ] && echo "  $f  [@jh.edu x$n]"
  done
  fail=1
fi

if [ $fail -ne 0 ]; then echo "check_public: FAILED (commit blocked)"; exit 1; fi
echo "check_public: OK ($(printf '%s\n' "$list" | wc -l | tr -d ' ') committable files checked, none private)"
