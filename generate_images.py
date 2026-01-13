#!/usr/bin/python3

import asyncio
from collections import defaultdict
from datetime import datetime
import os
import re

import aiohttp

from github_stats import Stats


################################################################################
# Helper Functions
################################################################################


def generate_output_folder() -> None:
    """
    Create the output folder if it does not already exist
    """
    if not os.path.isdir("generated"):
        os.mkdir("generated")


def group_by_month(days):
    """
    for activity graph function
    Group daily contribution data by month
    :param days: List of daily contribution records (date, count)
    :return: Dictionary mapping month number to list of contribution counts
    """
    months = defaultdict(list)
    for d in days:
        m = datetime.fromisoformat(d["date"]).month
        months[m].append(d["count"])
    return months


def compress_month(values, slots=4):
    """
    for activity graph function
    Compress a list of daily values into a fixed number of slots
    :param values: List of contribution counts for a month
    :param slots: Number of slots to compress into (default: 4)
    :return: List of aggregated values with fixed length
    """
    if not values:
        return [None] * slots

    size = len(values)
    step = size / slots
    buckets = []

    for i in range(slots):
        start = int(i * step)
        end = int((i + 1) * step)
        chunk = values[start:end]
        buckets.append(sum(chunk) if chunk else None)

    return buckets


def generate_bezier_path(points):
    """
    for activity graph function
    Generate an SVG cubic Bezier path from a list of points
    :param points: List of (x, y) coordinate tuples
    :return: SVG path string
    """
    if not points:
        return ""

    d = f"M{points[0][0]},{points[0][1]}"
    for i in range(1, len(points)):
        px, py = points[i - 1]
        x, y = points[i]
        cx = (px + x) / 2
        d += f"C{cx},{py},{cx},{y},{x},{y}"
    return d


def map_y(val, max_val):
    """
    for activity graph function
    Map a numeric value to an SVG Y-coordinate based on chart bounds
    :param val: Contribution value
    :param max_val: Maximum contribution value used for scaling
    :return: Y-coordinate in SVG space
    """
    TOP = 80
    BOTTOM = 350
    return BOTTOM - (val / max_val) * (BOTTOM - TOP)


################################################################################
# Individual Image Generation Functions
################################################################################


async def generate_overview(s: Stats) -> None:
    """
    Generate an SVG badge with summary statistics
    :param s: Represents user's GitHub statistics
    """
    with open("templates/overview.svg", "r") as f:
        output = f.read()

    output = re.sub("{{ name }}", await s.name, output)
    output = re.sub("{{ stars }}", f"{await s.stargazers:,}", output)
    output = re.sub("{{ forks }}", f"{await s.forks:,}", output)
    output = re.sub("{{ contributions }}", f"{await s.total_contributions:,}", output)
    changed = (await s.lines_changed)[0] + (await s.lines_changed)[1]
    output = re.sub("{{ lines_changed }}", f"{changed:,}", output)
    output = re.sub("{{ views }}", f"{await s.views:,}", output)
    output = re.sub("{{ repos }}", f"{len(await s.repos):,}", output)

    generate_output_folder()
    with open("generated/overview.svg", "w") as f:
        f.write(output)


async def generate_languages(s: Stats) -> None:
    """
    Generate an SVG badge with summary languages used
    :param s: Represents user's GitHub statistics
    """
    with open("templates/languages.svg", "r") as f:
        output = f.read()

    progress = ""
    lang_list = ""
    sorted_languages = sorted(
        (await s.languages).items(), reverse=True, key=lambda t: t[1].get("size")
    )
    delay_between = 150
    for i, (lang, data) in enumerate(sorted_languages):
        color = data.get("color")
        color = color if color is not None else "#000000"
        progress += (
            f'<span style="background-color: {color};'
            f'width: {data.get("prop", 0):0.3f}%;" '
            f'class="progress-item"></span>'
        )
        lang_list += f"""
                <li style="animation-delay: {i * delay_between}ms;">
                <svg xmlns="http://www.w3.org/2000/svg" class="octicon" style="fill:{color};"
                viewBox="0 0 16 16" version="1.1" width="16" height="16"><path
                fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8z"></path></svg>
                <span class="lang">{lang}</span>
                <span class="percent">{data.get("prop", 0):0.2f}%</span>
                </li>
            """

    output = re.sub(r"{{ progress }}", progress, output)
    output = re.sub(r"{{ lang_list }}", lang_list, output)

    generate_output_folder()
    with open("generated/languages.svg", "w") as f:
        f.write(output)


async def generate_recent_commits(s: Stats) -> None:
    with open("templates/recent_commits.svg", "r") as f:
        output = f.read()

    commits = await s.recent_commits(3)

    delay_step = 150
    items = ""

    for i, c in enumerate(commits):
        delay = i * delay_step
        badge = "<span class=\"badge\">latest</span>" if i == 0 else ""

        items += f"""
            <li style="animation-delay:{delay}ms">
            <div class="repo">
                <span class="dot"></span>
                <span class="text">{c["repo"]}</span>
                {badge}
            </div>
            <div class="commit">
                <span class="child-line"></span>
                <div>
                <span class="commit-msg">{c["message"]}</span>
                <span class="meta">
                    by {c["author"]} &#8226; {c["date"]}
                </span>
                </div>
            </div>
            </li>
            """

    output = re.sub(r"{{ commits }}", items, output)

    generate_output_folder()
    with open("generated/recent_commits.svg", "w") as f:
        f.write(output)


async def generate_activity_graph(s: Stats) -> None:
    """
    Generate an SVG graph visualizing yearly GitHub contribution activity
    :param s: Represents user's GitHub statistics
    """
    with open("templates/activity_graph.svg") as f:
        svg = f.read()

    days = await s.yearly_activity_daily(datetime.now().year)
    has_data = bool(days)
    months_data = group_by_month(days) if has_data else {}

    if has_data:
        last_date = max(datetime.fromisoformat(d["date"]) for d in days)
        year = last_date.year
        last_month = last_date.month
    else:
        year = datetime.now().year
        last_month = 0

    values = []
    for m in range(1, 13):
        if m > last_month:
            values.extend([None] * 4)
        else:
            values.extend(compress_month(months_data.get(m)))

    assert len(values) == 48

    X_START = 60
    X_END = 800
    TOP = 80
    BOTTOM = 350
    GRID_COUNT = 5

    STEP = (X_END - X_START) / 47
    valid_values = [v for v in values if v is not None]
    max_val = max(valid_values) if valid_values else 1

    # ===== Horizontal grid =====
    grid_h = ""
    for i in range(GRID_COUNT + 1):
        y = TOP + i * (BOTTOM - TOP) / GRID_COUNT
        grid_h += (
            f'<line x1="{X_START}" x2="{X_END}" '
            f'y1="{y}" y2="{y}" class="grid-h"/>\n'
        )

    # ===== Vertical grid =====
    grid_v = ""
    for i in range(48):
        x = X_START + i * STEP
        cls = "grid-month" if i % 4 == 0 else "grid-week"
        grid_v += (
            f'<line x1="{x}" y1="{TOP}" '
            f'x2="{x}" y2="{BOTTOM}" class="{cls}"/>\n'
        )

    # ===== Path =====
    points = [
        (X_START + i * STEP, map_y(v, max_val))
        for i, v in enumerate(values)
        if v is not None
    ]

    d = generate_bezier_path(points)

    # ===== Dots =====
    week_dots = ""
    main_dots = ""

    for i, v in enumerate(values):
        if v is None:
            continue
        x = X_START + i * STEP
        y = map_y(v, max_val)

        week_dots += (
            f'<line x1="{x}" y1="{y}" '
            f'x2="{x+0.01}" y2="{y}" class="ct-point-week"/>\n'
        )

        if v > 0:
            main_dots += (
                f'<line x1="{x}" y1="{y}" '
                f'x2="{x+0.01}" y2="{y}" class="ct-point-main"/>\n'
            )

    # ===== Month labels =====
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    labels = ""
    for i, m in enumerate(month_labels):
        x = X_START + (i * 4 + 2) * STEP
        labels += f'<text x="{x}" y="372" text-anchor="middle" class="ct-label">{m}</text>\n'

    # ===== Y Labels =====
    y_labels = []
    for i in range(GRID_COUNT + 1):
        value = int(max_val * (GRID_COUNT - i) / GRID_COUNT)
        y_labels.append(value)

    y_axis_labels = ""
    for i, val in enumerate(y_labels):
        y = TOP + i * (BOTTOM - TOP) / GRID_COUNT
        y_axis_labels += (
            f'<text x="{X_START - 10}" y="{y + 4}" '
            f'text-anchor="end" class="ct-label">{val}</text>\n'
        )

    # ===== Inject SVG =====
    svg = svg.replace("{{ TITLE }}", f"Contribution Activity ({year})")
    svg = svg.replace("{{ GRID_H }}", grid_h)
    svg = svg.replace("{{ GRID_V }}", grid_v)
    svg = svg.replace("{{ PATH }}", d)
    svg = svg.replace("{{ WEEK_DOTS }}", week_dots)
    svg = svg.replace("{{ MAIN_DOTS }}", main_dots)
    svg = svg.replace("{{ MONTH_LABELS }}", labels)
    svg = svg.replace("{{ Y_LABELS }}", y_axis_labels)

    generate_output_folder()
    with open("generated/activity_graph.svg", "w") as f:
        f.write(svg)


################################################################################
# Main Function
################################################################################


async def main() -> None:
    """
    Generate all badges
    """
    access_token = os.getenv("ACCESS_TOKEN")
    if not access_token:
        # access_token = os.getenv("GITHUB_TOKEN")
        raise Exception("A personal access token is required to proceed!")
    user = os.getenv("GITHUB_ACTOR")
    if user is None:
        raise RuntimeError("Environment variable GITHUB_ACTOR must be set.")
    exclude_repos = os.getenv("EXCLUDED")
    excluded_repos = (
        {x.strip() for x in exclude_repos.split(",")} if exclude_repos else None
    )
    exclude_langs = os.getenv("EXCLUDED_LANGS")
    excluded_langs = (
        {x.strip() for x in exclude_langs.split(",")} if exclude_langs else None
    )
    # Convert a truthy value to a Boolean
    raw_ignore_forked_repos = os.getenv("EXCLUDE_FORKED_REPOS")
    ignore_forked_repos = (
        not not raw_ignore_forked_repos
        and raw_ignore_forked_repos.strip().lower() != "false"
    )
    async with aiohttp.ClientSession() as session:
        s = Stats(
            user,
            access_token,
            session,
            exclude_repos=excluded_repos,
            exclude_langs=excluded_langs,
            ignore_forked_repos=ignore_forked_repos,
        )
        await asyncio.gather(
            generate_languages(s),
            generate_overview(s),
            generate_recent_commits(s),
            generate_activity_graph(s),
        )


if __name__ == "__main__":
    asyncio.run(main())
