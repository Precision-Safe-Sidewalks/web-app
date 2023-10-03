import re
import zipfile
from xml.etree import ElementTree

NS = {
    "": "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties",
    "ns": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "vt": "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes",
}


class Workbook:
    """Microsoft Excel workbook (minimal)"""

    def __init__(self, filename):
        self.filename = filename
        self.raw_data = {}
        self.worksheets = {}

        with zipfile.ZipFile(self.filename, "r") as f:
            for item in f.infolist():
                self.raw_data[item.filename] = f.read(item.filename)

    def get_sheet_names(self):
        """Return the list of sheet names"""
        data = self.raw_data["docProps/app.xml"]
        tree = ElementTree.fromstring(data)

        for node in tree.iter():
            if node.tag.endswith("TitlesOfParts"):
                sheets = node.findall(".//vt:lpstr", NS)
                return [s.text for s in sheets if "!Print" not in s.text]

        return []

    def update_cell(self, sheet_name, cell, value):
        """Update the cell data in a worksheet"""
        index = self.get_sheet_names().index(sheet_name) + 1
        arcname = f"xl/worksheets/sheet{index}.xml"

        data = self.raw_data[arcname].decode()
        pattern = f'<c r="{cell}"(.*?)(</c>|/>)'
        match = re.search(pattern, data, re.DOTALL)

        if match:
            text = match.group()
            cell = ElementTree.fromstring(text)

            for child in list(cell.iter())[1:]:
                cell.remove(child)

            if isinstance(value, (int, float)):
                v = ElementTree.SubElement(cell, "v")
                v.text = str(value)
            else:
                cell.set("t", "inlineStr")
                s = ElementTree.SubElement(cell, "is")
                t = ElementTree.SubElement(s, "t")
                t.text = str(value)

            repl = ElementTree.tostring(cell).decode()
            data = re.sub(pattern, repl, data, flags=re.DOTALL)
            self.raw_data[arcname] = data.encode("utf-8")

    def save(self, filename):
        """Save the Workbook to file"""

        with zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED) as f:
            for arcname, data in self.raw_data.items():
                f.writestr(arcname, data)
