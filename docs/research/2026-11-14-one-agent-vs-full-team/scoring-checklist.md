# Scoring checklist (written before either build; builders never see it)

Each row is pass/fail, checked by driving the finished app in a browser. A fail is one defect.

1. Opens from file:// with no network requests and no console errors.
2. Cannot start with fewer than 2 teams; cannot add a 7th team.
3. Blank name (empty and spaces-only) is refused.
4. Duplicate name refused, ignoring case and outer spaces ("Tigers" vs " tigers ").
5. Rounds default to 3; values outside 1..10 (0, 11) cannot be used.
6. Turn order follows the order teams were added and wraps round.
7. Countdown starts only on "Start timer", begins at 30, counts down.
8. "Sang it" adds 10 and then requires exactly one letter (rejects empty, "ab", "7"); the letter is shown to the next team.
9. "Passed" adds 0, turn moves on, letter unchanged.
10. Timeout at zero: -5, turn moves on by itself, letter unchanged; score may go below zero.
11. Undo after a "Sang it" restores score, turn and letter; a second Undo in a row does nothing (last turn only).
12. Undo after a timeout restores score and turn (and the timer does not fire a second penalty).
13. Game ends after exactly rounds x teams turns; winner shown.
14. Tie for first: says tie and names every tied team (test 2-way tie among 3 teams).
15. Refresh mid-game keeps scores, current team and letter.
16. "New game" asks for confirmation; cancel keeps the game, confirm clears it.
17. At 375 px wide: no horizontal scroll, main buttons at least 44 px tall, nothing clipped (setup, play and end screens).
18. After the game ends, turn buttons can no longer change scores (Undo of the final turn may be allowed).
