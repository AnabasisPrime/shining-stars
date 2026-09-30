import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT.joinpath("index.html").read_text(encoding="utf-8")
CSS = ROOT.joinpath("executive-network.css").read_text(encoding="utf-8")


class MemberCtaSystemTests(unittest.TestCase):
    def test_brad_approved_photo_is_local_and_used_for_all_rudolf_cards(self):
        photo = ROOT / "assets" / "brad-web-900.jpg"
        self.assertTrue(photo.is_file())
        self.assertGreater(photo.stat().st_size, 100_000)
        self.assertIn("'Rudolf Deas':'assets/brad-web-900.jpg'", HTML)
        self.assertIn("member-photo-brad", HTML)
        self.assertIn("object-position:center 34%", CSS)

    def test_public_data_model_accepts_optional_cta_columns(self):
        self.assertIn('"Secondary CTA URL": "secondaryCtaUrl"', HTML)
        self.assertIn('"Secondary CTA Label": "secondaryCtaLabel"', HTML)
        self.assertIn("function memberActionConfig(member={})", HTML)
        self.assertIn("approved.secondaryCtaUrl || member.secondaryCtaUrl || ''", HTML)
        self.assertIn("secondaryCtaUrl ?", HTML)

    def test_panescape_approved_actions_are_exact(self):
        self.assertIn("'liam connelley|panescape window cleaning'", HTML)
        self.assertIn("website: 'https://www.panescape.com/'", HTML)
        self.assertIn("secondaryCtaUrl: 'https://forms.gle/ERjWyxBCVVN4AftE8'", HTML)
        self.assertIn("secondaryCtaLabel: 'Get a Quote'", HTML)

    def test_card_and_profile_render_same_reusable_actions(self):
        self.assertGreaterEqual(HTML.count("actions.website ?"), 2)
        self.assertGreaterEqual(HTML.count("actions.secondaryCtaUrl ?"), 2)
        self.assertGreaterEqual(HTML.count('class="contact-btn member-website-btn'), 2)
        self.assertGreaterEqual(HTML.count('class="contact-btn member-cta-btn'), 2)

    def test_external_member_actions_use_safe_new_tab_contract(self):
        action_links = re.findall(
            r'<a class="contact-btn member-(?:website|cta)-btn"[^>]+>', HTML
        ) + re.findall(
            r'<a href="\$\{actions\.(?:website|secondaryCtaUrl)\}"[^>]+class="contact-btn member-(?:website|cta)-btn[^>]*>',
            HTML,
        )
        self.assertGreaterEqual(len(action_links), 4)
        for link in action_links:
            self.assertIn('target="_blank"', link)
            self.assertIn('rel="noopener noreferrer"', link)

    def test_cta_is_distinct_accessible_and_mobile_safe(self):
        self.assertIn(".member-cta-btn", CSS)
        self.assertIn("grid-column:1/-1", CSS)
        self.assertIn(".member-cta-btn:focus-visible", CSS)
        self.assertIn("@media (max-width:430px)", CSS)
        self.assertIn("grid-template-columns:repeat(2,minmax(0,1fr))", CSS)

    def test_public_private_email_guardrail_is_unchanged(self):
        self.assertNotIn("rbraddeas" + "@gmail.com", HTML.casefold())
        self.assertIn("RudolfDeas@Primerica.com", HTML)


if __name__ == "__main__":
    unittest.main()
