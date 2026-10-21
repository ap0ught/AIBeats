#!/bin/bash
# Re-fit the later-level segments onto a new upstream route (rngfit.py: Select re-rolls, wait repairs, briefing-page
# mash), one after another.
#   [SEGS="L8a L9a ..."] bash fitchain.sh <entry bookmark of the first segment> [tag, default g]
cd "$(dirname "$0")"
prev_end=$1; tag=${2:-g}
for seg in ${SEGS:-L8a L9a L10a L11a L12a L13a}; do
  out=${seg%?}$tag
  ids=; byt=
  case $seg in
    L8*) ids=7d ;;
    L11*) ids=7b ;;
    L12*) ids=5c,62 ;;
    L13*) byt=586 ;;
  esac
  RNGFIT_IDS=$ids RNGFIT_BYTES=$byt python rngfit.py $seg $prev_end $out > logs/fit_${seg}_$tag.txt 2>&1 || { echo "$seg STUCK: $(tail -1 logs/fit_${seg}_$tag.txt | cut -c1-200)"; exit 1; }
  echo "$seg done: $(tail -1 logs/fit_${seg}_$tag.txt | cut -c1-200)"
  prev_end=${out}_end
done
