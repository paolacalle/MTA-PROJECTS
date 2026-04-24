"""Helpers for running single-worksheet workbook enrichment scripts."""

from openpyxl import load_workbook


def run_single_sheet(input_path, output_path, transform):
    """Load the active sheet, apply a transform, and save the workbook."""
    workbook = load_workbook(input_path)
    worksheet = workbook.active
    transform(worksheet)
    workbook.save(output_path)
    print(f"Saved enriched file to: {output_path}")
