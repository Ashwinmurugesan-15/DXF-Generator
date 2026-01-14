from unittest.mock import MagicMock

from dxf_generator.drawing.exporter import export


def test_export_calls_saveas():
    doc = MagicMock()
    export(doc, "out.dxf")
    doc.saveas.assert_called_once_with("out.dxf")
