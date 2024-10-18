def is_time_overlap(new_start, new_end, existing_start, existing_end):
    """
    Check for intersection of time intervals. If the new interval (new_start, new_end) intersects with an existing
    interval (existing_start, existing_end), we return True.
    """
    return max(new_start, existing_start) < min(new_end, existing_end)
