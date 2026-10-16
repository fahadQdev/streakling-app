#!/bin/bash
# Full regression: functional suites, screen tours, random sessions. Logs in logs/run-*.log
cd "$(dirname "$0")"
mkdir -p logs
run() { timeout 1500 python3 "$@" > "logs/run-$(echo "$@" | tr ' /' '__').log" 2>&1; local rc=$?; echo "$(date +%T) exit $rc: $@" >> logs/progress.log; }
: > logs/progress.log
run t_logic.py & run t_habits.py & wait
run t_days.py & run t_hero.py & wait
run t_settings.py & run t_more.py & wait
run t_long.py & run t_pages.py & wait
for c in 390-light 390-dark 320-light; do run tour.py $c & done; wait
for c in 320-dark 360-light 375-light; do run tour.py $c & done; wait
for c in 430-light 430-dark 667x375-light; do run tour.py $c & done; wait
for c in 1280-light 1280-dark; do run tour.py $c & done; wait
for s in 9 10 11 12; do run t_monkey.py 200 $s & done; wait
for s in 13 14 15 16; do run t_monkey.py 200 $s & done; wait
echo ALLDONE >> logs/progress.log
