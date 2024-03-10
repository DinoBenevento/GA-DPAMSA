def is_overlap(range1, range2):
    from_row1, to_row1, from_column1, to_column1 = range1
    from_row2, to_row2, from_column2, to_column2 = range2

    # Check overlap
    overlap_row = from_row1 < to_row2 and to_row1 > from_row2
    overlap_column = from_column1 < to_column2 and to_column1 > from_column2

    return overlap_row and overlap_column

def check_overlap(new_range,used_ranges):
    for existing_range in used_ranges:
        if is_overlap(new_range, existing_range):
            return True  # I range si sovrappongono
    return False  # Nessuna sovrapposizione