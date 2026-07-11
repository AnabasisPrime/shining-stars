import re
import json
import unittest
from pathlib import Path


HTML = Path(__file__).resolve().parents[1].joinpath("index.html").read_text(encoding="utf-8")
PROOF_PATH = Path(__file__).with_name("browser_ordering_proof.json")


class PublicDirectoryContractTests(unittest.TestCase):
    def test_member_cards_include_more_info(self):
        self.assertIn('<summary>More Info</summary>', HTML)
        self.assertIn('class="member-more"', HTML)

    def test_pat_is_defensively_excluded(self):
        self.assertIn("includes('pat esposito')", HTML)

    def test_president_businesses_have_last_order_rule(self):
        self.assertIn("function isRudolfBusiness", HTML)
        self.assertIn("Number(isRudolfBusiness(a)) - Number(isRudolfBusiness(b))", HTML)
        self.assertIn("renderMemberGroups(leadershipMembers, true)", HTML)
        self.assertIn("function verifyPresidentOrdering", HTML)
        self.assertIn("highestNonPresidentIndex < lowestPresidentIndex", HTML)
        self.assertIn('data-president-owned="${isRudolfBusiness(member)}"', HTML)
        self.assertIn('id="alliance-leadership-businesses"', HTML)

    def test_rendered_indexes_put_every_president_business_last(self):
        proof = json.loads(PROOF_PATH.read_text(encoding="utf-8"))
        self.assertTrue(proof["passed"])
        self.assertLess(proof["highestNonRudolfIndex"], proof["lowestRudolfIndex"])
        self.assertEqual(
            ["Vivint", "Primerica", "PFS Investments Inc."],
            proof["presidentBusinesses"],
        )

    def test_accessibility_states_are_native_and_reduced_motion_exists(self):
        self.assertRegex(HTML, re.compile(r"<details class=\"member-more\">"))
        self.assertIn("prefers-reduced-motion: reduce", HTML)

    def test_spotlight_uses_helpful_resource_language(self):
        self.assertIn("How they can help", HTML)
        self.assertNotIn('<div class="spotlight-detail"><strong>Ideal referral</strong>', HTML)


if __name__ == "__main__":
    unittest.main()
