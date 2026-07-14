import re
import json
import unittest
from pathlib import Path


HTML = Path(__file__).resolve().parents[1].joinpath("index.html").read_text(encoding="utf-8")
CSS = Path(__file__).resolve().parents[1].joinpath("executive-network.css").read_text(encoding="utf-8")
PROOF_PATH = Path(__file__).with_name("browser_ordering_proof.json")


class PublicDirectoryContractTests(unittest.TestCase):
    def test_every_visitor_path_has_a_distinct_real_destination(self):
        block = re.search(r'<div class="journey-steps".*?</div>', HTML, re.S).group(0)
        self.assertIn('href="#site-home">Home</a>', block)
        self.assertIn('href="#members">Meet Our Members</a>', block)
        self.assertIn('data-dialog="professions-dialog">Open Professions</button>', block)
        self.assertIn('data-dialog="meeting-dialog">Visit a Meeting</button>', block)
        self.assertIn('href="#contact-leadership">Contact Leadership</a>', block)

    def test_visitor_paths_are_native_keyboard_controls(self):
        block = re.search(r'<div class="journey-steps".*?</div>', HTML, re.S).group(0)
        self.assertEqual(5, len(re.findall(r'class="journey-step"', block)))
        self.assertNotIn('tabindex="-1"', block.lower())
        self.assertIn('focus-visible', HTML)

    def test_public_links_have_no_placeholder_destinations(self):
        self.assertNotRegex(HTML, r'href\s*=\s*["\'](?:#|javascript:void\(0\))["\']')

    def test_leadership_inquiry_is_controlled_and_truthful(self):
        self.assertIn('id="leadership-inquiry-form"', HTML)
        for field_id in ("inquiry-name", "inquiry-email", "inquiry-subject", "inquiry-message"):
            self.assertRegex(HTML, rf'id="{field_id}"[^>]*required')
        self.assertIn('id="inquiry-phone"', HTML)
        self.assertIn('id="inquiry-phone" name="telephone"', HTML)
        self.assertIn('id="inquiry-company"', HTML)
        self.assertIn('Send Message', HTML)
        self.assertIn('No mailing-list enrollment is performed.', HTML)

    def test_contact_endpoint_is_production_ready(self):
        self.assertNotIn('CONTACT_ENDPOINT_PENDING_AUTHORIZATION', HTML)
        self.assertRegex(
            HTML,
            r"const CONTACT_ENDPOINT_URL = 'https://script\.google\.com/macros/s/[A-Za-z0-9_-]+/exec';",
        )
        self.assertIn("swfl-alliance-contact-result", HTML)
        self.assertIn("event.source !== inquiryTransport.contentWindow", HTML)
        self.assertIn('Your message could not be confirmed as submitted.', HTML)
        self.assertNotIn('Delivery could not be confirmed. Please try again; no success has been recorded.', HTML)
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
        self.assertIn('Extended profile coming soon', HTML)
        self.assertIn("'tracey von schmittou|preferred mediation llc'", HTML)
        self.assertIn("'liam connelley|panescape window cleaning'", HTML)
        self.assertIn("'dan donahoe|amac mortgage company'", HTML)

    def test_profile_dialog_has_keyboard_and_mobile_contracts(self):
        self.assertIn('<dialog class="profile-dialog"', HTML)
        self.assertIn('aria-label="Close member profile"', HTML)
        self.assertIn('@media (max-width:720px)', CSS)
        self.assertIn('dialog.showModal()', HTML)

    def test_executive_network_is_production_default(self):
        self.assertIn('<html lang="en" data-site-theme="executive-network">', HTML)
        self.assertIn('href="executive-network.css"', HTML)
        self.assertNotIn('URLSearchParams', HTML)
        self.assertNotIn('web-ux-003-preview.css', HTML)

    def test_visit_meeting_contract(self):
        self.assertIn('id="meeting-dialog"', HTML)
        self.assertIn('7:00 PM Eastern', HTML)
        self.assertIn('435 686 3146', HTML)
        self.assertIn('Password</dt><dd>1956', HTML)
        self.assertIn('Copy Meeting Details', HTML)

    def test_open_professions_are_directory_aware(self):
        self.assertIn('id="professions-dialog"', HTML)
        self.assertIn('function renderOpenProfessions', HTML)
        self.assertIn('professionOccupancyTerms', HTML)
        self.assertIn('Unique Businesses Welcome', HTML)

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
        self.assertIn("prefers-reduced-motion:reduce", CSS)

    def test_spotlight_uses_helpful_resource_language(self):
        self.assertIn("How they can help", HTML)
        self.assertNotIn('<div class="spotlight-detail"><strong>Ideal referral</strong>', HTML)


if __name__ == "__main__":
    unittest.main()
