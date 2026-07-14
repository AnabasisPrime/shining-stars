import re
import json
import unittest
from pathlib import Path


HTML = Path(__file__).resolve().parents[1].joinpath("index.html").read_text(encoding="utf-8")
PROOF_PATH = Path(__file__).with_name("browser_ordering_proof.json")


class PublicDirectoryContractTests(unittest.TestCase):
    def test_every_visitor_path_has_a_distinct_real_destination(self):
        block = re.search(r'<div class="journey-steps".*?</div>', HTML, re.S).group(0)
        links = re.findall(r'<a class="journey-step" href="#([^"]+)">([^<]+)</a>', block)
        self.assertEqual(
            [
                ("site-home", "Home"),
                ("members", "Meet Our Members"),
                ("open-professions", "Open Professions"),
                ("visit-meeting", "Visit a Meeting"),
                ("contact-leadership", "Contact Leadership"),
            ],
            links,
        )
        self.assertEqual(len(links), len({target for target, _ in links}))
        for target, _ in links:
            self.assertRegex(HTML, rf'id="{re.escape(target)}"')

    def test_visitor_paths_are_native_keyboard_controls(self):
        block = re.search(r'<div class="journey-steps".*?</div>', HTML, re.S).group(0)
        self.assertEqual(5, len(re.findall(r'<a class="journey-step" href="#[^"]+">', block)))
        self.assertNotIn('tabindex="-1"', block.lower())
        self.assertIn('a:focus-visible', HTML)

    def test_public_links_have_no_placeholder_destinations(self):
        self.assertNotRegex(HTML, r'href\s*=\s*["\'](?:#|javascript:void\(0\))["\']')

    def test_leadership_inquiry_is_controlled_and_truthful(self):
        self.assertIn('id="leadership-inquiry-form"', HTML)
        for field_id in ("inquiry-name", "inquiry-email", "inquiry-profession", "inquiry-interest", "inquiry-message"):
            self.assertRegex(HTML, rf'id="{field_id}"[^>]*required')
        self.assertIn('Nothing is sent automatically.', HTML)
        self.assertIn('Your inquiry is prepared below. Nothing has been sent.', HTML)
        self.assertIn("if (inquiry === lastPreparedInquiry) return;", HTML)
        self.assertNotIn('added to our mailing list', HTML.lower())

    def test_public_identity_is_southwest_florida(self):
        self.assertIn('serving Southwest Florida', HTML)
        self.assertIn('— Southwest Florida', HTML)

    def test_member_cards_include_more_info(self):
        self.assertIn('<summary>More Info</summary>', HTML)
        self.assertIn('class="member-more"', HTML)

    def test_full_profiles_are_member_specific_and_separate_from_more_info(self):
        self.assertIn('id="member-profile-dialog"', HTML)
        self.assertIn('aria-labelledby="member-profile-title"', HTML)
        self.assertIn('function openMemberProfileByIndex', HTML)
        self.assertIn('data-profile-index="${profileIndex}"', HTML)
        self.assertIn('aria-haspopup="dialog"', HTML)
        self.assertIn('<summary>More Info</summary>', HTML)
        self.assertNotIn('<a class="contact-btn" href="#members">Full Profile</a>', HTML)

    def test_unapproved_extended_profiles_have_truthful_fallback(self):
        self.assertIn('function hasApprovedPublicProfile', HTML)
        self.assertIn('Extended profile not available', HTML)

    def test_profile_dialog_has_keyboard_and_mobile_contracts(self):
        self.assertIn('<dialog class="profile-dialog"', HTML)
        self.assertIn('aria-label="Close member profile"', HTML)
        self.assertIn('@media (max-width:620px)', HTML)
        self.assertIn('dialog.showModal()', HTML)

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
            ["PFS Investments Inc.", "Primerica", "Vivint"],
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
