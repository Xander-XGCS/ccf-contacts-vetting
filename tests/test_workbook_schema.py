import unittest

from ccf_contact_vetting.workbook_schema import WORKBOOK_SCHEMA, schema_as_dict, schema_as_markdown


class WorkbookSchemaTests(unittest.TestCase):
    def test_tab_names_are_unique(self) -> None:
        names = [tab.name for tab in WORKBOOK_SCHEMA]
        self.assertEqual(len(names), len(set(names)))

    def test_column_names_are_unique_per_tab(self) -> None:
        for tab in WORKBOOK_SCHEMA:
            column_names = [column.name for column in tab.columns]
            self.assertEqual(len(column_names), len(set(column_names)), tab.name)

    def test_required_identifier_columns_exist(self) -> None:
        required_by_tab = {
            "People": "Person ID",
            "Drive Inventory": "Drive File ID",
            "Sync Runs": "Run ID",
            "Structure Suggestions": "Suggestion ID",
            "Companies": "Company ID",
            "Deals Projects": "Deal ID",
            "Relationships": "Relationship ID",
            "Research Queue": "Queue ID",
            "Sources": "Source ID",
            "Who Should Talk To Who": "Recommendation ID",
            "Review Log": "Review ID",
        }
        tabs = {tab.name: tab for tab in WORKBOOK_SCHEMA}
        for tab_name, column_name in required_by_tab.items():
            columns = {column.name: column for column in tabs[tab_name].columns}
            self.assertTrue(columns[column_name].required)

    def test_renderers_return_content(self) -> None:
        self.assertIn("tabs", schema_as_dict())
        self.assertIn("## People", schema_as_markdown())


if __name__ == "__main__":
    unittest.main()
