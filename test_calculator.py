import unittest

from Calculator import PLACEMENT_POINTS, app, calculate_standings


def result(team: str, placement: int | None, kills: int = 0) -> dict:
    return {"team": team, "placement": placement, "kills": kills}


def team(name: str, slot: int) -> dict:
    return {"name": name, "slot": slot}


def _twelve_team_five_match_payload() -> dict:
    names = [
        "Falcon",
        "Ember",
        "Nova",
        "Storm",
        "Viper",
        "Comet",
        "Titan",
        "Blaze",
        "Shadow",
        "Phoenix",
        "Orbit",
        "Raptor",
    ]
    placements_by_match = [
        [2, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        [3, 2, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        [5, 4, 3, 2, 1, 6, 7, 8, 9, 10, 11, 12],
        [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
    ]
    matches = []
    for match_number, placements in enumerate(placements_by_match, start=1):
        results = []
        for index, name in enumerate(names):
            kills = 1
            if (match_number, name) == (1, "Falcon"):
                kills = 40
            elif (match_number, name) == (2, "Falcon"):
                kills = 4
            elif (match_number, name) == (5, "Nova"):
                kills = 2
            results.append(result(name, placements[index], kills))
        matches.append({"results": results})
    return {
        "teams": [team(name, slot) for slot, name in enumerate(names, start=1)],
        "matches": matches,
    }


class CalculateStandingsTests(unittest.TestCase):
    def test_champion_rush_winner_takes_first_despite_lower_total_points(self):
        standings = calculate_standings(
            {
                "teams": [
                    team("Alpha", 1),
                    team("Bravo", 2),
                    team("Charlie", 3),
                ],
                "matches": [
                    {
                        "results": [
                            result("Alpha", 2, 51),
                            result("Bravo", 3, 51),
                            result("Charlie", 1),
                        ]
                    },
                    {
                        "results": [
                            result("Alpha", 1),
                            result("Bravo", 2, 6),
                            result("Charlie", 3),
                        ]
                    },
                ],
            }
        )

        self.assertEqual(
            [(row["rank"], row["team"]) for row in standings],
            [(1, "Alpha"), (2, "Bravo"), (3, "Charlie")],
        )
        self.assertEqual(standings[0]["total_points"], 72)
        self.assertGreater(standings[1]["total_points"], standings[0]["total_points"])
        self.assertGreater(standings[1]["total_points"], standings[2]["total_points"])
        self.assertEqual(standings[0]["tie_breaker"], "Champion Rush Winner")
        self.assertTrue(standings[0]["is_champion"])
        self.assertFalse(any(row["is_champion"] for row in standings[1:]))

    def test_booyah_in_match_that_reaches_60_does_not_win_champion_rush(self):
        standings = calculate_standings(
            {
                "teams": [team("Alpha", 1), team("Bravo", 2)],
                "matches": [
                    {
                        "results": [
                            result("Alpha", 1, 48),
                            result("Bravo", 2),
                        ]
                    },
                    {
                        "results": [
                            result("Alpha", 2),
                            result("Bravo", 1),
                        ]
                    },
                ],
            }
        )

        self.assertEqual(standings[0]["team"], "Alpha")
        self.assertFalse(any(row["is_champion"] for row in standings))

    def test_twelve_teams_across_five_matches_with_champion_rush(self):
        payload = _twelve_team_five_match_payload()
        standings = calculate_standings(payload)

        self.assertEqual(len(standings), 12)
        self.assertTrue(
            all(len(row["match_placements"]) == 5 for row in standings)
        )
        self.assertEqual(
            [(row["rank"], row["team"]) for row in standings[:3]],
            [(1, "Falcon"), (2, "Nova"), (3, "Ember")],
        )
        self.assertEqual(standings[0]["total_points"], 82)
        self.assertEqual(standings[0]["match_placements"], [2, 3, 1, 5, 12])
        self.assertTrue(standings[0]["is_champion"])
        falcon_match_totals = [
            sum(
                PLACEMENT_POINTS[row["placement"]] + row["kills"]
                for row in match["results"]
                if row["team"] == "Falcon"
            )
            for match in payload["matches"]
        ]
        self.assertEqual(
            [
                sum(falcon_match_totals[:match_number])
                for match_number in range(1, 6)
            ],
            [49, 61, 74, 81, 82],
        )

    def test_calculates_four_teams_across_five_matches(self):
        standings = calculate_standings(
            {
                "teams": [
                    team("Alpha", 1),
                    team("Bravo", 2),
                    team("Charlie", 3),
                    team("Delta", 4),
                ],
                "matches": [
                    {
                        "results": [
                            result("Alpha", 1, 5),
                            result("Bravo", 2, 3),
                            result("Charlie", 3, 2),
                            result("Delta", 4, 1),
                        ]
                    },
                    {
                        "results": [
                            result("Bravo", 1, 4),
                            result("Charlie", 2, 5),
                            result("Alpha", 3, 3),
                            result("Delta", 4, 2),
                        ]
                    },
                    {
                        "results": [
                            result("Charlie", 1, 6),
                            result("Delta", 2, 4),
                            result("Bravo", 3, 2),
                            result("Alpha", 4, 1),
                        ]
                    },
                    {
                        "results": [
                            result("Delta", 1, 5),
                            result("Alpha", 2, 4),
                            result("Bravo", 3, 3),
                            result("Charlie", 4, 2),
                        ]
                    },
                    {
                        "results": [
                            result("Bravo", 1, 7),
                            result("Alpha", 2, 2),
                            result("Charlie", 3, 4),
                            result("Delta", 4, 1),
                        ]
                    },
                ],
            }
        )

        self.assertEqual(len(standings), 4)
        self.assertTrue(
            all(len(row["match_placements"]) == 5 for row in standings)
        )
        self.assertEqual(
            [(row["team"], row["total_points"]) for row in standings],
            [("Bravo", 68), ("Charlie", 63), ("Alpha", 60), ("Delta", 55)],
        )

    def test_calculates_placement_kills_and_booyahs(self):
        standings = calculate_standings(
            {
                "teams": [team("Alpha", 7), team("Bravo", 2)],
                "matches": [
                    {"results": [result("Alpha", 1, 3), result("Bravo", 2, 4)]},
                    {"results": [result("Alpha", 2), result("Bravo", 1)]},
                ],
            }
        )

        self.assertEqual(
            [(row["team"], row["total_points"], row["booyahs"]) for row in standings],
            [("Bravo", 25, 1), ("Alpha", 24, 1)],
        )
        self.assertEqual(
            [row["match_placements"] for row in standings],
            [[2, 1], [1, 2]],
        )
        self.assertEqual(
            [(row["team"], row["slot"]) for row in standings],
            [("Bravo", 2), ("Alpha", 7)],
        )

    def test_breaks_equal_points_by_booyahs_then_kills(self):
        standings = calculate_standings(
            {
                "teams": [team("Alpha", 1), team("Bravo", 2), team("Charlie", 3)],
                "matches": [
                    {
                        "results": [
                            result("Alpha", 1),
                            result("Bravo", 2, 3),
                            result("Charlie", 3, 1),
                        ]
                    }
                ],
            }
        )

        self.assertEqual([row["team"] for row in standings], ["Alpha", "Bravo", "Charlie"])

    def test_uses_latest_shared_match_for_remaining_tie(self):
        standings = calculate_standings(
            {
                "teams": [team("Alpha", 8), team("Bravo", 3)],
                "matches": [
                    {"results": [result("Alpha", 1), result("Bravo", 2)]},
                    {"results": [result("Alpha", 2), result("Bravo", 1)]},
                ],
            }
        )

        self.assertEqual([row["team"] for row in standings], ["Bravo", "Alpha"])
        self.assertIn("Match 2", standings[0]["tie_breaker"])

    def test_keeps_teams_tied_without_a_shared_match(self):
        standings = calculate_standings(
            {
                "teams": [team("Alpha", 1), team("Bravo", 2)],
                "matches": [
                    {"results": [result("Alpha", 1)]},
                    {"results": [result("Bravo", 1)]},
                ],
            }
        )

        self.assertEqual([row["rank"] for row in standings], [1, 1])
        self.assertTrue(all(row["is_tied"] for row in standings))
        self.assertEqual(
            {row["team"]: row["match_placements"] for row in standings},
            {"Alpha": [1, None], "Bravo": [None, 1]},
        )

    def test_rejects_duplicate_placement(self):
        with self.assertRaisesRegex(ValueError, "used more than once"):
            calculate_standings(
                {
                    "teams": [team("Alpha", 1), team("Bravo", 2)],
                    "matches": [
                        {"results": [result("Alpha", 1), result("Bravo", 1)]}
                    ],
                }
            )

    def test_rejects_placement_above_number_of_teams_in_that_match(self):
        with self.assertRaisesRegex(ValueError, "placement in Match 2 must be between 1 and 2"):
            calculate_standings(
                {
                    "teams": [
                        team("Alpha", 1),
                        team("Bravo", 2),
                        team("Charlie", 3),
                    ],
                    "matches": [
                        {
                            "results": [
                                result("Alpha", 1),
                                result("Bravo", 2),
                                result("Charlie", 3),
                            ]
                        },
                        {
                            "results": [
                                result("Alpha", 1),
                                result("Bravo", 3),
                                result("Charlie", None),
                            ]
                        },
                    ],
                }
            )

    def test_rejects_kills_without_a_placement(self):
        with self.assertRaisesRegex(ValueError, "needs a placement"):
            calculate_standings(
                {
                    "teams": [team("Alpha", 1)],
                    "matches": [{"results": [result("Alpha", None, 2)]}],
                }
            )

    def test_rejects_duplicate_official_slot(self):
        with self.assertRaisesRegex(ValueError, "Slot 4 is assigned more than once"):
            calculate_standings(
                {
                    "teams": [team("Alpha", 4), team("Bravo", 4)],
                    "matches": [
                        {"results": [result("Alpha", 1), result("Bravo", 2)]}
                    ],
                }
            )

    def test_rejects_match_result_with_wrong_slot(self):
        with self.assertRaisesRegex(ValueError, "assigned to slot 4, not slot 2"):
            calculate_standings(
                {
                    "teams": [team("Alpha", 4)],
                    "matches": [
                        {"results": [{**result("Alpha", 1), "slot": 2}]}
                    ],
                }
            )


class CalculateEndpointTests(unittest.TestCase):
    def test_scoring_rules_page_is_served_as_html(self):
        response = app.test_client().get("/rules")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/html")
        self.assertIn(b"Placement points", response.data)
        self.assertIn(b"Champion Rush", response.data)
        response.close()

    def test_root_redirects_to_ui_folder_interface(self):
        response = app.test_client().get("/", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Teams and matches", response.data)
        self.assertNotIn(b"Free Fire Points", response.data)
        response.close()

    def test_ui_page_and_assets_are_served(self):
        client = app.test_client()

        page = client.get("/ui/")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"PT Calculator", page.data)
        page.close()

        script = client.get("/ui/app.js")
        self.assertEqual(script.status_code, 200)
        self.assertIn(b"match_standings", script.data)
        script.close()

    def test_six_teams_across_four_matches_rank_after_champion_rush(self):
        names = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot"]
        placements = [
            [4, 1, 2, 3, 5, 6],
            [1, 2, 3, 4, 5, 6],
            [6, 1, 2, 3, 4, 5],
            [6, 5, 4, 3, 2, 1],
        ]
        kills = [
            [53, 40, 0, 0, 1, 0],
            [0, 30, 0, 0, 1, 0],
            [0, 30, 0, 0, 1, 0],
            [0, 0, 0, 0, 1, 0],
        ]
        payload = {
            "teams": [team(name, slot) for slot, name in enumerate(names, start=1)],
            "matches": [
                {
                    "results": [
                        result(name, placements[match_index][team_index],
                               kills[match_index][team_index])
                        for team_index, name in enumerate(names)
                    ]
                }
                for match_index in range(4)
            ],
        }

        response = app.test_client().post("/calculate", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["match_standings"]), 4)
        self.assertEqual(
            [
                (row["rank"], row["team"], row["total_points"])
                for row in data["standings"]
            ],
            [
                (1, "Alpha", 82),
                (2, "Bravo", 139),
                (3, "Charlie", 33),
                (4, "Echo", 32),
                (5, "Delta", 31),
                (6, "Foxtrot", 28),
            ],
        )
        self.assertTrue(data["standings"][0]["is_champion"])
        self.assertFalse(data["match_standings"][0][0]["champion_rush_eligible"])
        alpha_second_match = next(
            row for row in data["match_standings"][1] if row["team"] == "Alpha"
        )
        self.assertTrue(alpha_second_match["champion_rush_eligible"])
        self.assertTrue(alpha_second_match["is_champion"])

    def test_marks_team_eligible_after_reaching_60_for_a_later_match(self):
        response = app.test_client().post(
            "/calculate",
            json={
                "teams": [team("Alpha", 1)],
                "matches": [{"results": [result("Alpha", 1, 48)]}],
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["match_standings"][0][0]["champion_rush_eligible"])
        self.assertTrue(data["standings"][0]["champion_rush_eligible"])
        self.assertFalse(data["standings"][0]["is_champion"])

    def test_marks_champion_rush_eligibility_before_later_matches(self):
        response = app.test_client().post(
            "/calculate",
            json={
                "teams": [team("Alpha", 1), team("Bravo", 2)],
                "matches": [
                    {
                        "results": [
                            result("Alpha", 2, 51),
                            result("Bravo", 1),
                        ]
                    },
                    {
                        "results": [
                            result("Alpha", 1),
                            result("Bravo", 2),
                        ]
                    },
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        alpha_first_match = next(
            row for row in data["match_standings"][0] if row["team"] == "Alpha"
        )
        alpha_second_match = next(
            row for row in data["match_standings"][1] if row["team"] == "Alpha"
        )
        alpha_overall = next(
            row for row in data["standings"] if row["team"] == "Alpha"
        )
        self.assertFalse(alpha_first_match["champion_rush_eligible"])
        self.assertTrue(alpha_second_match["champion_rush_eligible"])
        self.assertTrue(alpha_second_match["is_champion"])
        self.assertFalse(alpha_overall["champion_rush_eligible"])
        self.assertTrue(alpha_overall["is_champion"])

    def test_returns_separate_match_and_overall_standings(self):
        response = app.test_client().post(
            "/calculate",
            json={
                "teams": [team("Alpha", 1), team("Bravo", 2), team("Charlie", 3)],
                "matches": [
                    {
                        "results": [
                            result("Alpha", 1, 2),
                            result("Bravo", 2, 1),
                        ]
                    },
                    {
                        "results": [
                            result("Alpha", 2),
                            result("Bravo", 1),
                            result("Charlie", 3),
                        ]
                    },
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(
            [[row["team"] for row in match] for match in data["match_standings"]],
            [["Alpha", "Bravo"], ["Bravo", "Alpha", "Charlie"]],
        )
        self.assertEqual(
            [(row["team"], row["total_points"]) for row in data["standings"]],
            [("Alpha", 23), ("Bravo", 22), ("Charlie", 8)],
        )


if __name__ == "__main__":
    unittest.main()
