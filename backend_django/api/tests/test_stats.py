"""Pure-logic tests (no database needed)."""
import unittest
from datetime import date

from api import reporting, stats


def row(student, status, d, cls="A", subject="Math"):
    return {"student": student, "student_code": f"S{student}", "student_name": f"Student {student}",
            "class_name": cls, "course": 1, "subject": subject, "date": d, "status": status}


class StatsTests(unittest.TestCase):
    def setUp(self):
        # Monday 2026-11-02 and Monday 2026-11-09 are in different weeks
        self.rows = [
            row(1, "present", date(2026, 11, 2)), row(1, "present", date(2026, 11, 9)),
            row(2, "present", date(2026, 11, 2)), row(2, "absent", date(2026, 11, 9)),
            row(3, "absent", date(2026, 11, 2)), row(3, "absent", date(2026, 11, 9)),
            row(4, "late", date(2026, 11, 2)), row(4, "present", date(2026, 11, 9)),
        ]

    def test_rate_counts_late_as_attended(self):
        b = {"total": 4, "present": 2, "late": 1, "absent": 1}
        self.assertEqual(stats.attendance_rate(b), 75.0)
        self.assertEqual(stats.attendance_rate(b, late_counts=False), 50.0)
        self.assertIsNone(stats.attendance_rate({"total": 0, "present": 0, "late": 0, "absent": 0}))

    def test_summary(self):
        s = stats.summarize(self.rows)
        self.assertEqual(s["overall"]["total"], 8)
        self.assertEqual(s["overall"]["absent"], 3)
        self.assertEqual(s["overall"]["students"], 4)
        self.assertEqual(s["overall"]["rate"], 62.5)
        self.assertEqual([d["date"] for d in s["daily"]], ["2026-11-02", "2026-11-09"])

    def test_low_attendance(self):
        items = stats.low_attendance(self.rows, threshold=75)
        self.assertEqual([i["student"] for i in items], [3, 2])
        self.assertTrue(all(i["severity"] == "critical" for i in items))   # 0% and 50% are < 60
        items = stats.low_attendance(self.rows, threshold=60)
        self.assertEqual([i["severity"] for i in items], ["critical", "warning"])  # 0% < 48, 50% >= 48

    def test_trends(self):
        t = stats.trends(self.rows, period="week")
        self.assertEqual(len(t["series"]), 2)
        self.assertEqual(t["series"][0]["rate"], 75.0)
        self.assertEqual(t["series"][1]["rate"], 50.0)
        self.assertEqual(t["series"][1]["change"], -25.0)
        self.assertEqual(t["frequent_absentees"][0]["student"], 3)
        self.assertEqual([d["student"] for d in t["declining"]], [2])
        self.assertEqual(t["weekday"][0]["weekday"], "Monday")
        self.assertTrue(t["insights"])

    def test_trends_empty(self):
        t = stats.trends([])
        self.assertEqual(t["series"], [])
        self.assertEqual(t["insights"], [])


class ReportingTests(unittest.TestCase):
    def test_csv(self):
        data = reporting.build_csv(["A", "B"], [[1, None], ["x,y", 2]])
        self.assertTrue(data.startswith(b"\xef\xbb\xbf"))
        self.assertIn(b'"x,y"', data)

    def test_pdf_structure(self):
        rows = [[i, f"Student (name) {i}", "Present"] for i in range(200)]
        pdf = reporting.build_pdf("Report", "Generated", ["No", "Name", "Status"], rows)
        self.assertTrue(pdf.startswith(b"%PDF-1.4"))
        self.assertTrue(pdf.rstrip().endswith(b"%%EOF"))
        self.assertGreater(pdf.count(b"/Type /Page "), 1)       # paginated


if __name__ == "__main__":
    unittest.main()
