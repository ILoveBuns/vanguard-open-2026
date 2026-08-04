# Vanguard Open 2026 submission package

- Official deadline: 2026-09-25 23:59 Pacific Time.
- Prize pool: USD 1,000 ($500 / $300 / $200).
- Format selected: written work, maximum 2,500 words.
- `entry.md` includes the work, required sub-300-word rationale, AI disclosure,
  and entrant information.

The remaining boundary is personal review/authorship confirmation and final submission.
AI use is explicitly disclosed and the included disclosure must not be removed.

Install dependencies with `python3 -m pip install -r requirements.txt`, then run
`python3 build_pdf.py` to regenerate the PDF. Run `python3 validate_package.py`
before upload to recheck the 2,500-word entry
limit, 300-word rationale limit, AI disclosure, entrant fields, PDF readability,
page count, embedded title/author metadata and required rendered sections.

The generated PDF includes a vector map of the three classroom spaces and their
shared data boundary. The diagram is built directly with ReportLab, so it stays
sharp and reproducible without an external image asset.
