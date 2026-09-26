import json
import re
import unittest
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT.joinpath("index.html").read_text(encoding="utf-8")


class LaunchReadinessTests(unittest.TestCase):
    def test_public_page_has_complete_search_metadata(self):
        self.assertIn("<title>SWFL Strategic Referral Alliance |", HTML)
        description = re.search(r'<meta name="description" content="([^"]+)"', HTML)
        self.assertIsNotNone(description)
        self.assertGreaterEqual(len(description.group(1)), 80)
        self.assertIn('<link rel="canonical" href="https://anabasisprime.github.io/shining-stars/" />', HTML)
        self.assertIn('<meta name="robots" content="index,follow,max-image-preview:large" />', HTML)
        for property_name in ("og:title", "og:description", "og:url", "og:image"):
            self.assertIn(f'property="{property_name}"', HTML)
        self.assertIn('name="twitter:card" content="summary_large_image"', HTML)

    def test_one_clear_h1_and_semantic_landmarks(self):
        self.assertEqual(1, len(re.findall(r"<h1(?:\s|>)", HTML)))
        self.assertIn('<nav class="site-nav" aria-label="Primary navigation">', HTML)
        self.assertIn('<main id="members">', HTML)
        self.assertIn("<footer>", HTML)

    def test_organization_structured_data_is_truthful_and_parseable(self):
        match = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', HTML, re.S)
        self.assertIsNotNone(match)
        payload = json.loads(match.group(1))
        self.assertEqual("Organization", payload["@type"])
        self.assertEqual("SWFL Strategic Referral Alliance", payload["name"])
        self.assertEqual("Southwest Florida", payload["areaServed"]["name"])
        self.assertEqual("RudolfDeas@Primerica.com", payload["contactPoint"]["email"])

    def test_crawl_files_are_present_and_valid(self):
        robots = ROOT.joinpath("robots.txt").read_text(encoding="utf-8")
        self.assertIn("Allow: /", robots)
        self.assertIn("https://anabasisprime.github.io/shining-stars/sitemap.xml", robots)
        tree = ElementTree.parse(ROOT / "sitemap.xml")
        loc = tree.find("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        self.assertEqual("https://anabasisprime.github.io/shining-stars/", loc.text)

    def test_public_and_internal_email_roles_stay_separated(self):
        public_files = [ROOT / "index.html", ROOT / "404.html", ROOT / "robots.txt", ROOT / "sitemap.xml"]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in public_files)
        internal_only_email = "rbraddeas" + "@gmail.com"
        self.assertNotIn(internal_only_email, combined.casefold())
        self.assertIn("rudolfdeas@primerica.com", combined.casefold())

    def test_favicon_manifest_and_useful_404_exist(self):
        self.assertTrue((ROOT / "favicon.svg").is_file())
        manifest = json.loads((ROOT / "site.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual("SWFL Strategic Referral Alliance", manifest["name"])
        not_found = (ROOT / "404.html").read_text(encoding="utf-8")
        self.assertIn("Page Not Found | SWFL Strategic Referral Alliance", not_found)
        self.assertIn('href="/shining-stars/#members"', not_found)


if __name__ == "__main__":
    unittest.main()
