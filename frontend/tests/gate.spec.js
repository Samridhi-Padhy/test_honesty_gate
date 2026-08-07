import { expect, test } from "@playwright/test";

const PASSING_CONTRACT = {
    pr_id: "PR-200",
    verdict: "pass",
    mutants_tested: 5,
    mutants_caught: 5,
    mutants_survived: 0,
    results: [
        { mutant_id: "m1", operator: "equality_flip", location: "src/pricing.py:28", caught: true, explanation: "" },
        { mutant_id: "m2", operator: "boundary_shift", location: "src/pricing.py:15", caught: true, explanation: "" },
        { mutant_id: "m3", operator: "off_by_one", location: "src/pricing.py:37", caught: true, explanation: "" },
        { mutant_id: "m4", operator: "negate_boolean", location: "src/pricing.py:48", caught: true, explanation: "" },
        { mutant_id: "m5", operator: "drop_null_guard", location: "src/pricing.py:58", caught: true, explanation: "" },
    ],
    duration_ms: 1767,
};

const FAILING_CONTRACT = {
    pr_id: "PR-201",
    verdict: "fail",
    mutants_tested: 5,
    mutants_caught: 4,
    mutants_survived: 1,
    results: [
        { mutant_id: "m1", operator: "equality_flip", location: "src/pricing.py:28", caught: true, explanation: "" },
        { mutant_id: "m2", operator: "boundary_shift", location: "src/pricing.py:15", caught: true, explanation: "" },
        {
            mutant_id: "m3",
            operator: "off_by_one",
            location: "src/pricing.py:37",
            caught: false,
            explanation:
                "The test suite did not catch this off-by-one mutant. Add an assertion for the boundary case at the loop limit.",
        },
        { mutant_id: "m4", operator: "negate_boolean", location: "src/pricing.py:48", caught: true, explanation: "" },
        { mutant_id: "m5", operator: "drop_null_guard", location: "src/pricing.py:58", caught: true, explanation: "" },
    ],
    duration_ms: 1830,
};

async function stubGate(page, body, status = 200) {
    await page.route("**/gate*", (route) =>
        route.fulfill({
            status,
            contentType: "application/json",
            body: JSON.stringify(body),
        })
    );
}

test("pass state: shows merge allowed and marks every mutant caught", async ({ page }) => {
    await stubGate(page, PASSING_CONTRACT);
    await page.goto("/");

    const verdict = page.getByTestId("verdict");

    await expect(verdict).toContainText("Merge allowed");
    await expect(verdict).toHaveClass(/verdict-passed/);

    await expect(page.getByText("Survived", { exact: true })).toHaveCount(0);
    await expect(page.getByText("Caught", { exact: true })).toHaveCount(5);
});

test("fail state: shows merge blocked and marks one mutant survived", async ({ page }) => {
    await stubGate(page, FAILING_CONTRACT);
    await page.goto("/");

    const verdict = page.getByTestId("verdict");

    await expect(verdict).toContainText("Merge blocked");
    await expect(verdict).toHaveClass(/verdict-failed/);

    await expect(page.getByText("Survived", { exact: true })).toHaveCount(1);
    await expect(page.getByText("Caught", { exact: true })).toHaveCount(4);
});

test("error state: shows a retry instead of a blank screen", async ({ page }) => {
    await page.route("**/gate*", (route) => route.abort("failed"));
    await page.goto("/");

    await expect(page.getByTestId("error")).toBeVisible();
    await expect(page.getByTestId("retry")).toBeVisible();
});