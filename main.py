from bs4 import BeautifulSoup
from typing import OrderedDict
import re
from pprint import pprint


class Beatmap(OrderedDict):
    category: str
    title: str
    inneroni: bool
    rating: int
    bpm: tuple[float, float]
    
class TrainingEntry(OrderedDict):
    title: str
    inneroni: bool
    normalized_rating: int
    official_rating_descriptor: str
    training_category: str


def parse_beatmap_htmls() -> list[Beatmap]:
    def extract_category_table_from_html(html_path, genre) -> BeautifulSoup:
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

    def extract_beatmaps_from_category_table(category, table) -> list[Beatmap]:
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

        def parse_rating_cell(text) -> int | None:
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
            oni = parse_rating_cell(cols[7].get_text())
            inner_oni = parse_rating_cell(cols[8].get_text())

            beatmaps.append(
                Beatmap(
                    category=category,
                    title=title,
                    inneroni=False,
                    bpm=bpm,
                    rating=oni,
                )
            )

            if inner_oni is not None:
                beatmaps.append(
                    Beatmap(
                        category=category,
                        title=title,
                        inneroni=True,
                        bpm=bpm,
                        rating=inner_oni,
                    )
                )

        return beatmaps

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
        genre_table = extract_category_table_from_html(html_path, category)
        category_beatmaps = extract_beatmaps_from_category_table(category, genre_table)
        beatmaps.extend(category_beatmaps)

    return beatmaps

def parse_training_manual() -> list[str]:
    with open("オススメ練習曲一覧 - 太鼓の達人 譜面とか Wiki_.html", "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    training_entries = []
    
    categories = ['総合力', '体力・密度', '複合処理能力', '高速処理・アイマス譜面', '変則・技術譜面']
    official_difficulties_descriptor = []
    normalized_difficulty = 10
    
    # best effort parsing
    for t_body_idx, t_body in enumerate(soup.find_all("tbody")[6:61]):
        category = categories[t_body_idx % 5]
        if t_body_idx % 5 == 0:
            official_difficulties_descriptor = []
        for t_row_idx, t_row in enumerate(t_body.find_all("tr")[1:]):
            t_data = t_row.find_all('td')
            if t_body_idx % 5 == 0: # row with "難易度"
                official_difficulties_descriptor.append(t_data[0].get_text())
            for beatmap_anchor in t_row.find_all('td')[1 if t_body_idx % 5 == 0 else 0].find_all('a'):
                training_entries.append(TrainingEntry(
                    title=beatmap_anchor.get_text(),
                    inneroni=False, # to be filled later
                    normalized_rating=normalized_difficulty,
                    official_rating_descriptor=official_difficulties_descriptor[t_row_idx],
                    training_category=category,
                ))
        if t_body_idx % 5 == 4:
            normalized_difficulty -= 1
            
    return training_entries
    

def main():
    beatmaps = parse_beatmap_htmls()
    training_entries = parse_training_manual()

if __name__ == "__main__":
    main()
