from bs4 import BeautifulSoup


def get_soup(url) -> BeautifulSoup:
    with open("/mnt/c/temp/laserflip.html") as f:
        return BeautifulSoup(f.read(), "html.parser")


""""
function category(dom: CheerioStatic) {
    return dom("#gdc").text();
}

function originalTitle(dom: CheerioStatic) {
    return dom("#gd2 #gj").text();
}

function length(dom: CheerioStatic) {
    const table = dom("#gdd table");
    const value = table.find("tr").eq(5).children(".gdt2").text();
    return Number(value.split(' ')[0]);
}
"""


def load_overview(url):
    soup = get_soup(url)
    title = soup.select_one("#gn").text
    original_title = soup.select_one("#gj").text

    lengthStr = soup.select_one("#gdd tr:nth-child(6) td:nth-child(2)").text
    length = lengthStr.split(" ")[0]
    print(title, original_title, length)


load_overview("")

