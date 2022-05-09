import seaborn


def calculate_gap(ascent, distance, duration):
    ratio = 1000 / distance

    adjusted_ascent = ascent * ratio
    adjusted_duration = duration * ratio

    gap = adjusted_duration

    remaining_ascent = adjusted_ascent % 50
    remaining_reduction = remaining_ascent * 0.9

    if adjusted_ascent > 50:
        gap -= 45
        remaining_reduction = remaining_ascent * 1.2
    if adjusted_ascent > 100:
        gap -= 60
        remaining_reduction = remaining_ascent * 1.5
    if adjusted_ascent > 150:
        gap -= 75
        remaining_reduction = remaining_ascent * 1.8
    if adjusted_ascent >= 200:
        gap -= 90
        return round(gap * (0.995 ** (adjusted_ascent - 200)))
    return round(gap - remaining_reduction)
