"""Free Fire match-point calculator based on the EWC 2026 rulebook."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template_string, request, send_file

PLACEMENT_POINTS = {
    1: 12,
    2: 9,
    3: 8,
    4: 7,
    5: 6,
    6: 5,
    7: 4,
    8: 3,
    9: 2,
    10: 1,
    11: 0,
    12: 0,
}
MAX_TEAMS = 12
RULES_FILE = Path(__file__).with_name("README.md")

app = Flask(__name__)

PAGE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Free Fire | Tournament Points</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0c111b;
      --panel: #151d2b;
      --panel-soft: #1b2636;
      --line: #2c394c;
      --text: #f3f6fb;
      --muted: #9ba9bc;
      --accent: #ff9f43;
      --accent-strong: #ff7b32;
      --green: #63d6a2;
      --red: #ff8181;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: radial-gradient(ellipse at 82% 0%, #233148 0, var(--bg) 42rem);
      color: var(--text);
      font: 15px/1.5 "Segoe UI", Arial, sans-serif;
    }
    main { width: min(1120px, calc(100% - 32px)); margin: 42px auto 64px; }
    .topline { display: flex; justify-content: space-between; align-items: center; gap: 20px; }
    .eyebrow { color: var(--accent); font-size: 12px; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }
    h1 { margin: 6px 0 8px; font-size: clamp(30px, 5vw, 46px); line-height: 1.1; }
    h2 { margin: 0; font-size: 20px; }
    p { margin: 0; color: var(--muted); }
    .intro { max-width: 650px; }
    .button, button {
      display: inline-flex; align-items: center; justify-content: center; gap: 8px;
      border: 1px solid var(--line); border-radius: 9px; padding: 10px 15px;
      background: var(--panel-soft); color: var(--text); font: inherit; font-weight: 700;
      text-decoration: none; cursor: pointer; transition: .15s ease;
    }
    .button:hover, button:hover { border-color: var(--accent); transform: translateY(-1px); }
    button.primary { color: #201408; border-color: var(--accent); background: var(--accent); }
    button.primary:hover { background: var(--accent-strong); }
    button.danger { color: var(--red); }
    button.small { padding: 6px 10px; font-size: 13px; }
    .panel {
      margin-top: 24px; padding: 22px; border: 1px solid var(--line);
      border-radius: 15px; background: color-mix(in srgb, var(--panel) 94%, transparent);
      box-shadow: 0 16px 38px #0002;
    }
    .panel-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 16px; }
    .section-number { margin-right: 8px; color: var(--accent); font-size: 13px; }
    label { display: block; margin-bottom: 7px; color: #d7dfeb; font-size: 13px; font-weight: 700; }
    textarea, input {
      width: 100%; border: 1px solid var(--line); border-radius: 8px;
      background: #0e1520; color: var(--text); font: inherit; outline: none;
    }
    textarea { min-height: 150px; padding: 12px; resize: vertical; }
    input { min-width: 0; padding: 8px 10px; }
    textarea:focus, input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px #ff9f4320; }
    input[type="number"] { width: 88px; }
    .hint { margin-top: 7px; font-size: 13px; }
    .toolbar { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
    .game { margin-top: 14px; padding: 16px; border: 1px solid var(--line); border-radius: 11px; background: #111925; }
    .game-title { margin: 0; font-size: 16px; }
    .table-wrap { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; text-align: left; }
    th { padding: 11px 12px; color: var(--muted); font-size: 12px; letter-spacing: .04em; text-transform: uppercase; }
    td { padding: 12px; border-top: 1px solid var(--line); }
    .entry-table th, .entry-table td, .roster-table th, .roster-table td { padding: 8px 10px; }
    .entry-table th:not(:nth-child(2)), .entry-table td:not(:nth-child(2)),
    .roster-table th:first-child, .roster-table td:first-child { text-align: center; }
    .entry-table input[type="number"], .roster-table input[type="number"] { text-align: center; }
    .team-name { font-weight: 700; }
    .result-table tbody tr:first-child td { border-top-color: transparent; }
    .total { font-size: 18px; font-weight: 800; }
    .badge { display: inline-block; padding: 3px 8px; border-radius: 999px; background: #63d6a21a; color: var(--green); font-size: 12px; font-weight: 700; }
    .tie { color: #ffd18c; }
    .empty { padding: 24px 12px; color: var(--muted); text-align: center; }
    .message { display: none; margin-top: 16px; padding: 12px 14px; border-radius: 8px; }
    .message.error { display: block; color: #ffd1d1; border: 1px solid #9c4c56; background: #48232a; }
    .message.success { display: block; color: #c8ffe6; border: 1px solid #36745b; background: #173a2d; }
    .footer-note { margin-top: 16px; font-size: 12px; }
    [hidden] { display: none !important; }
    @media (max-width: 650px) {
      main { width: min(100% - 20px, 1120px); margin-top: 24px; }
      .topline { align-items: flex-start; flex-direction: column; }
      .panel { padding: 15px; }
      .panel-head { align-items: flex-start; }
      th, td { padding: 10px 8px; }
    }
  </style>
</head>
<body>
<main>
  <header class="topline">
    <div>
      <div class="eyebrow">Tournament toolkit</div>
      <h1>Free Fire Points</h1>
      <p class="intro">Enter match placements and kills to calculate the live standings and apply the official tie-break order.</p>
    </div>
    <a class="button" href="/rules" target="_blank" rel="noopener">View rule <span aria-hidden="true">↗</span></a>
  </header>

  <section class="panel">
    <div class="panel-head">
      <div><h2><span class="section-number">01</span>Team slots</h2><p class="hint">Enter each official slot number and its assigned team name. Up to 12 slots.</p></div>
    </div>
    <div class="table-wrap">
      <table class="roster-table">
        <thead><tr><th>Slot</th><th>Team name</th><th></th></tr></thead>
        <tbody id="roster"></tbody>
      </table>
    </div>
    <div class="toolbar">
      <button id="add-team" type="button">＋ Add team slot</button>
      <button id="add-match" class="primary" type="button">＋ Add match</button>
      <button id="reset" type="button">Reset all</button>
    </div>
    <div id="matches"></div>
    <div id="message" class="message" role="status" aria-live="polite"></div>
    <div class="toolbar">
      <button id="calculate" class="primary" type="button">Calculate standings</button>
    </div>
    <p class="footer-note">Placement points and tie-break rules follow the attached Free Fire at EWC 2026 rulebook.</p>
  </section>

  <section id="standings-panel" class="panel" hidden>
    <div class="panel-head">
      <div><h2><span class="section-number">02</span>Leaderboard</h2><p id="summary" class="hint"></p></div>
    </div>
    <div class="table-wrap">
      <table class="result-table">
        <thead id="standings-head"></thead>
        <tbody id="standings"></tbody>
      </table>
    </div>
  </section>
</main>
<script>
  const roster = document.getElementById("roster");
  const matchesContainer = document.getElementById("matches");
  const message = document.getElementById("message");
  const standingsPanel = document.getElementById("standings-panel");
  let matchCount = 0;

  function showMessage(text, kind) {
    message.textContent = text;
    message.className = "message " + kind;
  }

  function addTeamRow(slotValue = null) {
    if (roster.querySelectorAll("tr").length >= 12) {
      showMessage("The rulebook placement table supports up to 12 team slots.", "error");
      return;
    }
    if (slotValue === null) {
      const assignedSlots = new Set(
        [...roster.querySelectorAll(".roster-slot")].map(input => Number(input.value))
      );
      slotValue = Array.from({ length: 12 }, (_, index) => index + 1)
        .find(number => !assignedSlots.has(number)) || "";
    }
    const row = document.createElement("tr");
    const slotCell = document.createElement("td");
    const slot = document.createElement("input");
    slot.type = "number";
    slot.min = "1";
    slot.max = "12";
    slot.step = "1";
    slot.value = slotValue;
    slot.placeholder = "1–12";
    slot.className = "roster-slot";
    slot.setAttribute("aria-label", "Official slot number");
    slotCell.append(slot);

    const nameCell = document.createElement("td");
    const name = document.createElement("input");
    name.type = "text";
    name.maxLength = 40;
    name.placeholder = "Team name";
    name.className = "roster-team";
    name.setAttribute("aria-label", "Team name");
    name.addEventListener("keydown", event => {
      if (event.key !== "Enter") return;
      event.preventDefault();

      const rows = [...roster.querySelectorAll("tr")];
      const nextRow = rows[rows.indexOf(row) + 1];
      if (nextRow) {
        nextRow.querySelector(".roster-team").focus();
      } else if (rows.length < 12) {
        addTeamRow();
        roster.lastElementChild.querySelector(".roster-team").focus();
      }
    });
    nameCell.append(name);

    const removeCell = document.createElement("td");
    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "small danger remove-team";
    remove.textContent = "Remove";
    remove.addEventListener("click", () => row.remove());
    removeCell.append(remove);
    row.append(slotCell, nameCell, removeCell);
    roster.append(row);
  }

  function getTeams() {
    const rows = [...roster.querySelectorAll("tr")];
    if (!rows.length) throw new Error("Add at least one team slot.");
    const teams = rows.map(row => {
      const slot = row.querySelector(".roster-slot").value.trim();
      const name = row.querySelector(".roster-team").value.trim();
      if (!slot || !name) throw new Error("Enter both a slot number and team name for every row.");
      const number = Number(slot);
      if (!Number.isInteger(number) || number < 1 || number > 12) {
        throw new Error("Slot numbers must be whole numbers from 1 to 12.");
      }
      return { slot: number, name };
    }).sort((a, b) => a.slot - b.slot);
    if (new Set(teams.map(team => team.slot)).size !== teams.length) {
      throw new Error("Each official slot number can only be used once.");
    }
    if (new Set(teams.map(team => team.name.toLocaleLowerCase())).size !== teams.length) {
      throw new Error("Team names must be unique.");
    }
    return teams;
  }

  function addMatch() {
    let teams;
    try {
      teams = getTeams();
    } catch (error) {
      showMessage(error.message, "error");
      return;
    }

    matchCount += 1;
    roster.querySelectorAll("input, .remove-team").forEach(field => { field.disabled = true; });
    document.getElementById("add-team").disabled = true;
    const card = document.createElement("section");
    card.className = "game";
    card.dataset.match = String(matchCount);
    const head = document.createElement("div");
    head.className = "panel-head";
    const title = document.createElement("h3");
    title.className = "game-title";
    title.textContent = "Match " + matchCount;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "small danger";
    remove.textContent = "Remove";
    remove.addEventListener("click", () => {
      card.remove();
      if (!matchesContainer.querySelector(".game")) {
        roster.querySelectorAll("input, .remove-team").forEach(field => { field.disabled = false; });
        document.getElementById("add-team").disabled = false;
      }
      renumberMatches();
    });
    head.append(title, remove);
    const wrap = document.createElement("div");
    wrap.className = "table-wrap";
    const table = document.createElement("table");
    table.className = "entry-table";
    table.innerHTML = "<thead><tr><th>Slot</th><th>Team</th><th>Placement</th><th>Kills</th></tr></thead>";
    const body = document.createElement("tbody");
    teams.forEach(team => {
      const row = document.createElement("tr");
      const slot = document.createElement("td");
      slot.textContent = team.slot;
      const name = document.createElement("td");
      name.className = "team-name";
      name.textContent = team.name;
      const placementCell = document.createElement("td");
      const placement = document.createElement("input");
      placement.type = "number";
      placement.min = "1";
      placement.max = "12";
      placement.step = "1";
      placement.placeholder = "—";
      placement.setAttribute("aria-label", team.name + " placement");
      placement.className = "placement";
      placement.addEventListener("keydown", event => {
        if (event.key === "Enter") {
          event.preventDefault();
          row.querySelector(".kills").focus();
        }
      });
      placementCell.append(placement);
      const killsCell = document.createElement("td");
      const kills = document.createElement("input");
      kills.type = "text";
      kills.inputMode = "numeric";
      kills.min = "0";
      kills.value = "0";
      kills.setAttribute("aria-label", team.name + " kills");
      kills.className = "kills";
      kills.addEventListener("keydown", event => {
        if (event.key !== "Enter") return;
        event.preventDefault();
        const values = kills.value.trim();
        if (!/^\d+(?:\s*\+\s*\d+)*$/.test(values)) {
          showMessage("Enter kills as whole numbers, for example 1+2+6+9.", "error");
          return;
        }
        kills.value = String(values.split("+").reduce((total, value) => total + Number(value.trim()), 0));
        message.className = "message";
      });
      killsCell.append(kills);
      row.append(slot, name, placementCell, killsCell);
      body.append(row);
    });
    table.append(body);
    wrap.append(table);
    card.append(head, wrap);
    matchesContainer.append(card);
    standingsPanel.hidden = true;
    message.className = "message";
    card.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function renumberMatches() {
    [...matchesContainer.querySelectorAll(".game")].forEach((card, index) => {
      card.dataset.match = String(index + 1);
      card.querySelector(".game-title").textContent = "Match " + (index + 1);
    });
  }

  function getPayload() {
    const teams = getTeams();
    const matches = [...matchesContainer.querySelectorAll(".game")].map(card => ({
      results: [...card.querySelectorAll("tbody tr")].map(row => ({
        team: row.querySelector(".team-name").textContent,
        slot: Number(row.cells[0].textContent),
        placement: row.querySelector(".placement").value,
        kills: row.querySelector(".kills").value
      }))
    }));
    return { teams, matches };
  }

  function renderStandings(rows, matchCount) {
    const body = document.getElementById("standings");
    const header = document.getElementById("standings-head");
    const headingRow = document.createElement("tr");
    ["Slot", "Team", ...Array.from({ length: matchCount }, (_, index) => "Match " + (index + 1)),
      "Booyahs", "Place pts", "Kills", "Total", "Tie-break"
    ].forEach(label => {
      const th = document.createElement("th");
      th.textContent = label;
      headingRow.append(th);
    });
    header.replaceChildren(headingRow);
    body.replaceChildren();
    rows.forEach(row => {
      const tr = document.createElement("tr");
      const cells = [
        { text: row.slot },
        { text: row.team, className: "team-name" },
        ...row.match_placements.map(placement => ({
          text: placement === null ? "—" : placement
        })),
        { text: row.booyahs },
        { text: row.placement_points },
        { text: row.kills },
        { text: row.total_points, className: "total" }
      ];
      cells.forEach(item => {
        const td = document.createElement("td");
        td.textContent = item.text;
        if (item.className) td.className = item.className;
        tr.append(td);
      });
      const tie = document.createElement("td");
      if (row.tie_breaker === "Winner") {
        const badge = document.createElement("span");
        badge.className = "badge";
        badge.textContent = "Winner";
        tie.append(badge);
      } else {
        tie.textContent = row.tie_breaker;
        if (row.is_tied) tie.className = "tie";
      }
      tr.append(tie);
      body.append(tr);
    });
    document.getElementById("summary").textContent =
      rows.length + " teams · " + matchCount + " matches · total = placement points + kills";
    standingsPanel.hidden = false;
  }

  document.getElementById("add-team").addEventListener("click", () => addTeamRow());
  document.getElementById("add-match").addEventListener("click", addMatch);
  document.getElementById("reset").addEventListener("click", () => window.location.reload());
  document.getElementById("calculate").addEventListener("click", async () => {
    message.className = "message";
    try {
      const response = await fetch("/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(getPayload())
      });
      const result = await response.json();
      if (!response.ok) {
        showMessage(result.error || "Could not calculate standings.", "error");
        return;
      }
      renderStandings(result.standings, result.match_count);
      showMessage("Standings calculated successfully.", "success");
    } catch (error) {
      showMessage(error instanceof TypeError
        ? "Could not reach the calculator. Check that the Python server is running."
        : error.message, "error");
    }
  });
  addTeamRow(1);
</script>
</body>
</html>
"""


def _read_integer(value: Any, label: str, minimum: int, maximum: int | None = None) -> int:
    """Parse an integer from a JSON or form value and validate its range."""
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a whole number.")
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be a whole number.") from None
    if str(value).strip() != str(number):
        raise ValueError(f"{label} must be a whole number.")
    if number < minimum or (maximum is not None and number > maximum):
        if maximum is None:
            raise ValueError(f"{label} cannot be less than {minimum}.")
        raise ValueError(f"{label} must be between {minimum} and {maximum}.")
    return number


def calculate_standings(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate match input and return standings using the rulebook tie-breaks."""
    teams = payload.get("teams")
    matches = payload.get("matches")
    if not isinstance(teams, list) or not teams:
        raise ValueError("Enter at least one team.")
    if len(teams) > MAX_TEAMS:
        raise ValueError("The rulebook placement table supports up to 12 teams.")

    normalized_teams: list[dict[str, Any]] = []
    seen_teams: set[str] = set()
    seen_slots: set[int] = set()
    for index, team in enumerate(teams, start=1):
        if isinstance(team, str):
            name_value = team
            slot_value = index
        elif isinstance(team, dict):
            name_value = team.get("name")
            slot_value = team.get("slot")
        else:
            raise ValueError("Each team must include a slot number and team name.")
        if not isinstance(name_value, str) or not name_value.strip():
            raise ValueError("Team names cannot be empty.")
        name = name_value.strip()
        if len(name) > 40:
            raise ValueError("Team names must be 40 characters or fewer.")
        key = name.casefold()
        if key in seen_teams:
            raise ValueError("Team names must be unique.")
        slot = _read_integer(slot_value, f"{name}'s slot number", 1, MAX_TEAMS)
        if slot in seen_slots:
            raise ValueError(f"Slot {slot} is assigned more than once.")
        seen_teams.add(key)
        seen_slots.add(slot)
        normalized_teams.append({"name": name, "slot": slot})

    if not isinstance(matches, list) or not matches:
        raise ValueError("Add at least one match before calculating.")

    team_keys = {team["name"].casefold(): team["name"] for team in normalized_teams}
    team_slots = {team["name"]: team["slot"] for team in normalized_teams}
    stats = {
        team["name"]: {
            "team": team["name"],
            "slot": team["slot"],
            "placement_points": 0,
            "kills": 0,
            "booyahs": 0,
            "total_points": 0,
            "match_placements": {},
        }
        for team in normalized_teams
    }

    for match_number, match in enumerate(matches, start=1):
        if not isinstance(match, dict) or not isinstance(match.get("results"), list):
            raise ValueError(f"Match {match_number} has invalid results.")
        used_teams: set[str] = set()
        used_placements: set[int] = set()
        played = 0
        for result in match["results"]:
            if not isinstance(result, dict):
                raise ValueError(f"Match {match_number} contains an invalid team result.")
            raw_team = result.get("team")
            if not isinstance(raw_team, str) or raw_team.casefold() not in team_keys:
                raise ValueError(f"Match {match_number} contains an unknown team.")
            team = team_keys[raw_team.casefold()]
            if team in used_teams:
                raise ValueError(f"{team} is listed more than once in Match {match_number}.")
            used_teams.add(team)
            if "slot" in result:
                result_slot = _read_integer(
                    result["slot"], f"{team}'s slot in Match {match_number}", 1, MAX_TEAMS
                )
                if result_slot != team_slots[team]:
                    raise ValueError(
                        f"{team} is assigned to slot {team_slots[team]}, not slot {result_slot}."
                    )

            placement_value = result.get("placement")
            kills_value = result.get("kills", 0)
            if placement_value is None or placement_value == "":
                kills = _read_integer(kills_value, f"{team}'s kills in Match {match_number}", 0)
                if kills:
                    raise ValueError(f"{team} needs a placement if kills are entered in Match {match_number}.")
                continue

            placement = _read_integer(
                placement_value, f"{team}'s placement in Match {match_number}", 1, MAX_TEAMS
            )
            if placement in used_placements:
                raise ValueError(f"Placement {placement} is used more than once in Match {match_number}.")
            used_placements.add(placement)
            kills = _read_integer(kills_value, f"{team}'s kills in Match {match_number}", 0)

            row = stats[team]
            row["placement_points"] += PLACEMENT_POINTS[placement]
            row["kills"] += kills
            row["total_points"] += PLACEMENT_POINTS[placement] + kills
            row["booyahs"] += placement == 1
            row["match_placements"][match_number] = placement
            played += 1
        if not played:
            raise ValueError(f"Enter at least one placement for Match {match_number}.")

    inactive = [
        team["name"] for team in normalized_teams
        if not stats[team["name"]]["match_placements"]
    ]
    if inactive:
        raise ValueError(f"Enter a result for each team at least once: {', '.join(inactive)}.")

    base_sorted = sorted(
        stats.values(),
        key=lambda row: (row["total_points"], row["booyahs"], row["kills"]),
        reverse=True,
    )
    grouped: list[list[dict[str, Any]]] = []
    for row in base_sorted:
        key = (row["total_points"], row["booyahs"], row["kills"])
        if grouped:
            previous = grouped[-1][0]
            previous_key = (previous["total_points"], previous["booyahs"], previous["kills"])
            if key == previous_key:
                grouped[-1].append(row)
                continue
        grouped.append([row])

    standings: list[dict[str, Any]] = []
    next_rank = 1
    for group in grouped:
        shared_match = None
        if len(group) > 1:
            shared_match = next(
                (
                    match_number
                    for match_number in range(len(matches), 0, -1)
                    if all(match_number in row["match_placements"] for row in group)
                ),
                None,
            )
            if shared_match is not None:
                group.sort(key=lambda row: row["match_placements"][shared_match])

        unresolved_tie = len(group) > 1 and shared_match is None
        for row in group:
            if len(group) == 1:
                tie_breaker = "Winner" if next_rank == 1 else "—"
            elif shared_match is None:
                tie_breaker = "Still tied — no shared match"
            else:
                tie_breaker = f"Match {shared_match}: placed {row['match_placements'][shared_match]}"
            standings.append(
                {
                    "rank": next_rank,
                    "team": row["team"],
                    "slot": row["slot"],
                    "match_placements": [
                        row["match_placements"].get(match_number)
                        for match_number in range(1, len(matches) + 1)
                    ],
                    "booyahs": row["booyahs"],
                    "placement_points": row["placement_points"],
                    "kills": row["kills"],
                    "total_points": row["total_points"],
                    "tie_breaker": tie_breaker,
                    "is_tied": unresolved_tie,
                }
            )
        next_rank += len(group)

    return standings


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.get("/rules")
def rules():
    return send_file(RULES_FILE, mimetype="text/markdown")


@app.post("/calculate")
def calculate():
    payload = request.get_json()
    if not isinstance(payload, dict):
        return jsonify(error="Request body must be a JSON object."), 400
    try:
        standings = calculate_standings(payload)
    except ValueError as error:
        return jsonify(error=str(error)), 400
    return jsonify(standings=standings, match_count=len(payload["matches"]))


if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=False,
    )