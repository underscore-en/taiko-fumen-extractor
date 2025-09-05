from bs4 import BeautifulSoup
from typing import OrderedDict
import re
from pprint import pprint


class Beatmap(OrderedDict):
    category: str
    title: str
    inneroni: bool
    stars: int
    bpm: tuple[float, float]
    note: str


def extract_genre_table(html_path, genre) -> BeautifulSoup:
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")

    wikiwiki_tablesorter_wrappers = soup.find_all(
        "div", class_="wikiwiki-tablesorter-wrapper"
    )

    for wrapper in wikiwiki_tablesorter_wrappers:
        table = wrapper.find("table")
        if table.find("ins", string=genre):
            return table

    assert False, f"Failed to find table for genre {genre} in {html_path}"


def parse_category_table(category, table) -> list[Beatmap]:
    def parse_bpm_cell(text) -> tuple[float, float] | None:
        numbers = re.findall(r"\d+(?:\.\d+)?", text)
        if len(numbers) == 1:
            n = float(numbers[0])
            return (n, n)
        elif len(numbers) >= 2:
            n1 = float(numbers[0])
            n2 = float(numbers[1])
            return (n1, n2)
        return None

    def parse_stars_cell(text) -> int | None:
        match = re.search(r"★×(\d+)", text)
        if match:
            return int(match.group(1))
        return None

    beatmaps: list[Beatmap] = []
    tbody = table.find("tbody")
    for row in tbody.find_all("tr"):
        cols = row.find_all("td")
        assert len(cols) == 9
        title = cols[2].find("strong").get_text()
        bpm = parse_bpm_cell(cols[3].get_text())
        oni = parse_stars_cell(cols[7].get_text())
        inner_oni = parse_stars_cell(cols[8].get_text())

        beatmaps.append(
            Beatmap(
                category=category,
                title=title,
                inneroni=False,
                bpm=bpm,
                stars=oni,
            )
        )

        if inner_oni is not None:
            beatmaps.append(
                Beatmap(
                    category=category,
                    title=title,
                    inneroni=True,
                    bpm=bpm,
                    stars=inner_oni,
                )
            )

    return beatmaps


def parse_beatmap_htmls() -> list[Beatmap]:
    main_html_path = "太鼓の達人 ニジイロVer. 2025 ＜正式名称：2020年3月Ver.＞ （V61.06） - 太鼓の達人 譜面とか Wiki_.html"
    namco_html_path = "作品_新AC_ナムコオリジナル - 太鼓の達人 譜面とか Wiki_.html"

    beatmaps: list[Beatmap] = []

    for category, html_path in (
        ("ポップス", main_html_path),
        ("キッズ", main_html_path),
        ("アニメ", main_html_path),
        ("ボーカロイド™曲", main_html_path),
        ("ゲームミュージック", main_html_path),
        ("バラエティ", main_html_path),
        ("クラシック", main_html_path),
        ("ナムコオリジナル", namco_html_path),
    ):
        genre_table = extract_genre_table(html_path, category)
        category_beatmaps = parse_category_table(category, genre_table)
        beatmaps.extend(category_beatmaps)
        
    return beatmaps

def main():
    beatmaps = parse_beatmap_htmls()
    pprint(beatmaps)

if __name__ == "__main__":
    main()
