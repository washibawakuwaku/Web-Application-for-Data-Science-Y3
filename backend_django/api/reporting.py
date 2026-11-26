"""CSV and PDF export (feature 7). Pure Python – no third-party PDF library needed."""
import csv
import io


def build_csv(columns, rows):
    """UTF-8 with BOM so Excel opens Khmer / accented names correctly."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(columns)
    for row in rows:
        writer.writerow(["" if v is None else v for v in row])
    return ("\ufeff" + buf.getvalue()).encode("utf-8")


def _esc(text):
    text = str(text).encode("latin-1", "replace").decode("latin-1")     # base-14 fonts are Latin-1 only
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf(title, subtitle, columns, rows):
    """A simple paginated A4-landscape table. Returns PDF bytes."""
    page_w, page_h, margin = 842, 595, 36
    font, line_h = 8, 11
    max_chars = int((page_w - 2 * margin) / (0.6 * font))               # Courier: 0.6 em per char
    gap = 2

    table = [[("" if v is None else str(v)) for v in row] for row in rows]
    widths = [max([len(str(c))] + [len(r[i]) for r in table]) for i, c in enumerate(columns)]
    widths = [min(w, 28) for w in widths]
    budget = max_chars - gap * (len(columns) - 1)
    if sum(widths) > budget:
        scale = budget / sum(widths)
        widths = [max(4, int(w * scale)) for w in widths]

    def fmt(values):
        return (" " * gap).join(str(v)[:w].ljust(w) for v, w in zip(values, widths))

    header = fmt(columns)
    body_top = page_h - margin - 52
    lines_per_page = max(1, int((body_top - margin - 14) / line_h) - 2)
    chunks = [table[i:i + lines_per_page] for i in range(0, len(table), lines_per_page)] or [[]]

    objects = [None] * (5 + 2 * len(chunks))                            # 1-based ids -> index id-1
    objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    kids = " ".join(f"{7 + 2 * i} 0 R" for i in range(len(chunks)))
    objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(chunks)} >>".encode()
    objects[2] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>"
    objects[3] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"
    objects[4] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold /Encoding /WinAnsiEncoding >>"

    for i, chunk in enumerate(chunks):
        ops = [
            f"BT /F2 14 Tf {margin} {page_h - margin - 10} Td ({_esc(title)}) Tj ET",
            f"BT /F1 9 Tf {margin} {page_h - margin - 26} Td ({_esc(subtitle)}) Tj ET",
            f"BT /F3 {font} Tf {margin} {body_top} Td ({_esc(header)}) Tj ET",
            f"{margin} {body_top - 3} m {page_w - margin} {body_top - 3} l S",
        ]
        y = body_top - line_h - 2
        for row in chunk:
            ops.append(f"BT /F1 {font} Tf {margin} {y} Td ({_esc(fmt(row))}) Tj ET")
            y -= line_h
        ops.append(f"BT /F1 8 Tf {page_w - margin - 60} {margin - 14} Td (Page {i + 1} of {len(chunks)}) Tj ET")
        stream = "\n".join(ops).encode("latin-1", "replace")
        objects[5 + 2 * i] = b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream"
        objects[6 + 2 * i] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_w} {page_h}] "
            f"/Contents {6 + 2 * i} 0 R /Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R >> >> >>"
        ).encode()

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for n, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{n} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)
