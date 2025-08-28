from tabulate import tabulate

def tabulate_rows(rows, headers, max_rows=10):
    display_rows = rows[:max_rows]
    return tabulate(display_rows, headers=headers, tablefmt="github", floatfmt=".2f")
