import requests
import re
import json
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


def request_to_url(url: str, headers: dict) -> requests.Response:

    """
    Get the html text from input url
    :param url: string type
    :return: the request object
    """

    try:
        r_obj = requests.get(url=url, headers=headers)

        # if something wrong exists, then raises the error and jump to except block
        r_obj.raise_for_status()

        return r_obj

    except HTTPError:
        print("Warning: A HTTP Error Occurs!")


def construct_headers(url: str) -> dict:
    return {
        "referer": url,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 Edg/85.0.564.67"
    }


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
        overview_tags = soup.find_all(name="span", attrs={"class": "desc-info-text"})
        overview = overview_tags[0].text.strip()
        # print(overview)
    except IndexError:
        overview = ""
        print("The video doesn't have the overview")

    # get some episode of the video
    # but the captured lis contain nothing
        # episode_lis = soup.find(name="ul", class_="list-box").find_all(name="li")
        # print(episode_lis)

    # try to read the raw text of soup_obj
        # print(html.prettify())

    # find out that the video_page information is in the <script> label
    script = ""
    for current_script in soup.find_all(name="script"):
        if current_script.text.startswith("window.__INITIAL_STATE__"):
            script = current_script.text

    script = script.replace("window.__INITIAL_STATE__=", "")
    subbed_script = re.compile(r"({.*});").search(script).group(1)
    # print(subbed_script)

    # transform the json to python dict
    json_obj = json.loads(subbed_script)
    pages = json_obj["videoData"]["pages"]

    page_dict = {}
    for item in pages:
        page = item["page"]
        page_title = item["part"]
        page_dict[page] = page_title

    # print(page_dict)

    return {
        "title": title,
        "date": date,
        "tags": tags,
        "overview": overview,
        "episodes": page_dict
    }


def get_video_and_audio(website_html: str, headers: dict):

    # look for the <script> that contains the video and audio
    soup = BeautifulSoup(
        markup=website_html,
        features="html.parser"
    )

    target_script = ""
    for script in soup.find_all(name="script"):
        if script.text.startswith("window.__playinfo__"):
            target_script = script.text.replace("window.__playinfo__=", "")

    # transform the json to python dict
    json_obj = json.loads(target_script)

    # extract the url of the video and audio (default: extract the first video and audio)
    video_url = json_obj["data"]["dash"]["video"][0]["baseUrl"]
    video_content = request_to_url(url=video_url, headers=headers).content

    audio_url = json_obj["data"]["dash"]["audio"][0]["baseUrl"]
    audio_content = request_to_url(url=audio_url, headers=headers).content

    # store the data of the captured video and audio
    with open("video.m4s", "wb") as v_obj:
        v_obj.write(video_content)

    with open("audio.m4s", "wb") as a_obj:
        a_obj.write(audio_content)

    print("finished!")


def main(bv_id: str):
    # concatenate the protocol and domain with bv_id
    url = construct_url(bv_id=bv_id)

    # construct the header to request
    headers = construct_headers(url=url)

    # send the request to the url server
    html = request_to_url(url, headers=headers).text

    # get the title, episodes. date, tags, overview
    get_text_information(html=html)

    get_video_and_audio(website_html=html, headers=headers)


if __name__ == "__main__":

    bv_id = "BV19B4y1W76i"
    main(bv_id=bv_id)
