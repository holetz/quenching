"""The `github` backend carries `dependsOn` as native issue dependencies ("blocked by").

Every case runs offline: the pure helpers take plain data, and the backend cases further down
drive a strict request-driven double of `gh api` patched over `_gh_run`. No test reaches a
real repository.
"""

import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.backends.azure import azure_predecessor_ids
from quenching.specs.backends.github import (
    GH_DEPENDENCY_LIMIT,
    github_blocked_by,
    github_dependency_diff,
    github_dependency_limit_refusal,
)


class PureDependencies(unittest.TestCase):
    def test_wanted_ids_keep_numeric_non_self_in_order_without_duplicates(self):
        fm = {"dependsOn": ["30", "slug", "owner/repo#4", "7", "30", "12"]}
        self.assertEqual([30, 7], azure_predecessor_ids(fm, 12))

    def test_the_current_set_comes_from_a_blocked_by_listing_page_or_pages(self):
        page = [{"number": 3, "id": 903}, {"number": 5, "id": 905}, {"title": "no number"}]
        self.assertEqual({3: 903, 5: 905}, github_blocked_by(page))
        self.assertEqual({3: 903, 5: 905}, github_blocked_by([page[:1], page[1:]]))
        self.assertEqual({}, github_blocked_by([]))
        self.assertEqual({}, github_blocked_by(None))

    def test_add_remove_and_no_op(self):
        current = {3: 903, 5: 905}
        self.assertEqual(([7], []), github_dependency_diff(current, [3, 5, 7]))
        self.assertEqual(([], [3]), github_dependency_diff(current, [5]))
        self.assertEqual(([7], [3, 5]), github_dependency_diff(current, [7]))
        self.assertEqual(([], []), github_dependency_diff(current, [5, 3]))
        self.assertEqual(([], []), github_dependency_diff({}, []))

    def test_over_the_limit_refuses_and_at_the_limit_does_not(self):
        at = list(range(1, GH_DEPENDENCY_LIMIT + 1))
        self.assertIsNone(github_dependency_limit_refusal(9, at))
        refusal = github_dependency_limit_refusal(9, at + [GH_DEPENDENCY_LIMIT + 1])
        self.assertEqual(("sp-gh-dependency-limit", 2), (refusal["code"], refusal["exit"]))
        self.assertIn("#9", refusal["message"])
        self.assertIn("new issue", github_dependency_limit_refusal(None, at + [999])["message"])


if __name__ == "__main__":
    unittest.main()
