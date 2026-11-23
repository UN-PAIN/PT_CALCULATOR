import unittest

from Calculator import calculate_standings


def result(team: str, placement: int | None, kills: int = 0) -> dict:
    return {"team": team, "placement": placement, "kills": kills}


def team(name: str, slot: int) -> dict:
    return {"name": name, "slot": slot}


class CalculateStandingsTests(unittest.TestCase):
    def test_calculates_placement_kills_and_booyahs(self):
        standings = calculate_standings(
            {
                "teams": [team("Alpha", 7), team("Bravo", 2)],
                "matches": [
                    {"results": [result("Alpha", 1, 3), result("Bravo", 2, 4)]},
                    {"results": [result("Alpha", 10), result("Bravo", 1)]},
                ],
            }
        )

        self.assertEqual(
            [(row["team"], row["total_points"], row["booyahs"]) for row in standings],
            [("Bravo", 25, 1), ("Alpha", 16, 1)],
        )
        self.assertEqual(
            [row["match_placements"] for row in standings],
            [[2, 1], [1, 10]],
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
                    {"results": [result("Alpha", 2), result("Bravo", 3)]},
                    {"results": [result("Alpha", 3), result("Bravo", 2)]},
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


if __name__ == "__main__":
    unittest.main()
