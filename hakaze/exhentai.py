from bs4 import BeautifulSoup
import re


def get_soup(url) -> BeautifulSoup:
    with open("/mnt/c/temp/laserflip.html") as f:
        return BeautifulSoup(f.read(), "html.parser")


def parse_tags(soup):
    divs = soup.select("#taglist tbody div")
    tags = {}
    for div in divs:
        parts = (div["id"][3:]).split(":")[::-1]
        if parts[0] not in tags:
            tags[parts[0]] = []
        if len(parts) == 1:
            tags[parts[0]].append("misc")
        else:
            tags[parts[0]].append(parts[1])
    return tags


def load_overview(url):
    soup = get_soup(url)
    title = soup.select_one("#gn").text
    original_title = soup.select_one("#gj").text

    lengthStr = soup.select_one("#gdd tr:nth-child(6) td:nth-child(2)").text
    length = lengthStr.split(" ")[0]

    regex = re.compile("\/g\/([\d\w]+)\/([\d\w]+)")
    match = regex.search(url)
    if match.lastindex < 2:
        raise ValueError(f"Could not parse dir from [{url}]")
    dirname = f"{match.group(1)}.{match.group(2)}"

    tags = parse_tags(soup)


# print(match.group(1))

