def frame_to_time(frame, fps=60):
    total_seconds = frame / fps
    minute = int(total_seconds / 60)
    second = int(total_seconds % 60)
    if minute >= 60:
        hour = int(minute / 60)
        minute = int(minute % 60)
        return f'{hour:02d}:{minute:02d}:{second:02d}'
    else:
        return f'{minute:02d}:{second:02d}'
