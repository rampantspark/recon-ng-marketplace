# module required for framework integration
from recon.core.module import BaseModule
# mixins for desired functionality
from recon.mixins.resolver import ResolverMixin
from recon.mixins.threads import ThreadingMixin
# module specific imports
import os
import codecs

class Module(BaseModule, ResolverMixin, ThreadingMixin):

    meta = {
        "name": "Markdown Report Generator",
        "author": "Anthony Lyons (@rampantspark)",
        "version": "1.0",
        "description": "Generates a report in markdown format (compatible with Obsidian, GitBook, etc.)",
        "options": (
            ("sanitize", True, True, "mask sensitive data in the report"),
            ("customer", None, True, "use customer name in the report header"),
            ("creator", None, True, "use creator name in the report footer"),
            (
                "filename",
                os.path.join(BaseModule.workspace, "results.md"),
                True,
                "path and filename for report output",
            ),
        ),
    }

    def module_run(self):
        # Get a list of database tables
        tables = self.get_tables()

        # Create the combined Markdown report file
        output_file = self.options['filename']
        customer = self.options['customer']
        creator = self.options['creator']

        with open(output_file, 'w', encoding='utf-8') as markdown_file:
            # Write a header to the combined report
            markdown_file.write("# Report\n")
            markdown_file.write("Prepared for: \n")
            markdown_file.write(customer + "\n")
            markdown_file.write("Prepared by: \n")
            markdown_file.write(creator + "\n\n")

            # Loop through each table and append its content as a Markdown
            # table
            for table in tables:
                markdown_content = self.generate_markdown_for_table(table)
                markdown_file.write(markdown_content)

        self.output(f"Combined Markdown report generated in '{output_file}'.")

    def generate_markdown_for_table(self, table):
        # Fetch data from the database table
        rows = self.query(f'SELECT * FROM "{table}"')
        columns = [x[1] for x in self.query(f"PRAGMA table_info('{table}')")]

        # Create a Markdown table header
        markdown_content = f"## {table} \n\n"
        markdown_content += "| " + " | ".join(columns) + " |\n"
        markdown_content += "| " + " | ".join(["---"] * len(columns)) + " |\n"

        # Iterate through rows and append them as Markdown table rows
        for row in rows:
            row_values = [
                self.html_escape(f"[[{str(x) if x is not None else ''}]]")
            for x in row
                    ]
            markdown_content += "| " + " | ".join(row_values) + " |\n"

        markdown_content += "\n"

        return markdown_content
