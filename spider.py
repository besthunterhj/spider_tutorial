import requests
from bs4 import BeautifulSoup
from requests import HTTPError


def construct_url(bv_id: str) -> str:
    """
    Construct the url of the target video from bilibili
    :param bv_id: the id of the target video
    :return: a full url of the target video
    """

    auxiliary = "https://www.bilibili.com/video/"

    return auxiliary + bv_id


def request_to_url(url: str) -> requests.Response:

    """
    Get the html text from input url
    :param url: string type
    :return: the request object
    """

    try:
        r_obj = requests.get(url=url)

        # if something wrong exists, then raises the error and jump to except block
        r_obj.raise_for_status()

        return r_obj

    except HTTPError:
        print("Warning: A HTTP Error Occurs!")


def get_text_information(html: str) -> dict:

    soup = BeautifulSoup(
        markup=html,
        features="html.parser"
    )

    # get the title of the video
    # the type of the h1_tags [bs4.element.Tag]
    h1_tags = soup.find_all(name="h1")
    title = h1_tags[0].text

    # The attributes of bs4.element.Tag object:  ["attribute_name"] .text .name
    # print(h1_tags[0]["class"])

    # get the upload time of the video
    span_tags = soup.find_all(name="span", attrs={"class": "pudate-text"})
    date = span_tags[0].text.strip()

    # get the tags of the video
    ul = soup.find(name="ul", class_="tag-area")
    video_tags = ul.find_all_next(name="li", class_="tag")
    tags = [
        tag.text.strip() for tag in video_tags
    ]

    # get the overview of the video
    # maybe the overview doesn't exist, so it's necessary to catch the indexError
    try:
        overview_tags = soup.find_all(name="span", attrs={"class", "desc-info-text"})
        overview = overview_tags[0].text.strip()
        print(overview)
    except IndexError:
        overview = ""
        print("The video doesn't have the overview")

    return {
        "title": title,
        "date": date,
        "tags": tags,
        "overview": overview
    }


if __name__ == "__main__":

    url = construct_url("BV19B4y1W76i")
    html = request_to_url(url).text

    get_text_information(html=html)





