def export(doc, filepath: str):
    # Save the generated DXF document to the given file path
    doc.saveas(filepath)
