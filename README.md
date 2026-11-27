# Free Fire Tournament Rules

## Web interface

Run `python Calculator.py` from the `PT_CALCULATOR` folder. It starts the local server and opens the interface in your browser.

To build a Windows application folder, run `build_windows.bat`. It creates `Executable\PTCalculator\PTCalculator.exe`; launch the executable to start the calculator and open its interface. Building requires Python and pip, and the script installs the build tools from `requirements-build.txt`.

The web interface in the sibling `UI` folder uses the calculator's `/calculate` endpoint. When running from source, it is also available directly at `http://127.0.0.1:5000/ui/`.

Scoring and tie-breaks are based on the **Free Fire at EWC 2026 Official Rulebook**, sections 5.4 and 5.5.

## Point distribution

Each match awards placement points and kill points:

- **Each kill is worth 1 point.**
- Placement points are awarded as follows:

  | Placement | Points |
  |---:|---:|
  | 1st | 12 |
  | 2nd | 9 |
  | 3rd | 8 |
  | 4th | 7 |
  | 5th | 6 |
  | 6th | 5 |
  | 7th | 4 |
  | 8th | 3 |
  | 9th | 2 |
  | 10th | 1 |
  | 11th | 0 |
  | 12th | 0 |

**Match total = placement points + kills.** A team's tournament total is the sum of its match totals. A Booyah is recorded for each 1st-place finish.

The calculator supports up to 12 teams per match, matching the placement table in the rulebook. Enter each team's official slot number (1–12) and assigned name in the Team slots section. Slot numbers must be unique; the leaderboard and match entry show each team under its assigned slot. Leave placement blank for a team that did not play that match; that team must have zero kills for that match.

## Champion Rush

Champion Rush unlocks for a team after it finishes a match with at least 60 cumulative points. To win, that team must earn a Booyah in a later match; a Booyah in the same match where it first reaches 60 points does not count. The first team to meet both conditions is the Champion Rush winner and is ranked first, regardless of total points. All other teams are ordered by total points, applying the tie-break order below when needed.

## Tie-break order

When teams have the same total points, apply these criteria in order:

1. **Most Booyahs** across the phase.
2. **Most accumulated kills** across the phase.
3. **Best placement in the latest match shared by all tied teams.** The calculator searches backward for the latest match in which every team in that tied group has a placement, then ranks them by those placements.

If tied teams have no match in which they all played, the calculator leaves them tied rather than inventing another rule. Refer the unresolved tie to tournament administration.

## Entering match results

1. Add each participating team with its official slot number and team name. Use no more than 12 unique slots. Pressing Enter in a team-name field moves to the next team-name field, adding a row with the next available slot when needed.
2. Select **Add match** for each game.
3. Enter each participating team's placement (1–12) and kill count. A blank placement means the team did not play.
4. Select **Calculate standings**. Invalid or duplicate slots, placements, and other input errors are reported on the page.

Each match must have at least one placement, and every listed team must have a result in at least one match.

## Leaderboards and results

After calculating, the page shows a separate leaderboard for each match and an overall standings leaderboard. Each leaderboard has independent **Share result**, **Save result**, and show/hide controls. Sharing uses the browser's share feature when available, otherwise it copies the result to the clipboard; saving downloads that leaderboard as a CSV file. Use **Add match** below the leaderboards to enter another game.

## Rulebook reference

**Free Fire at EWC 2026 Official Rulebook**, section 5.4 “Match Scoring” and section 5.5 “Tiebreakers” (printed pages 21–22).
