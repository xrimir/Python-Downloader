import threading
import validators
import PySimpleGUI as sg
import requests
import time
import mimetypes

col = [
    [sg.Text('Url: '), sg.Input(key="urlInput")],
    [sg.Text('Name: '), sg.Input(key="nameInput")],
    [sg.Text('_' * 80)],
    [sg.Text("Downloading Progress: "), sg.Text("N/A", key="progressField", size=(30, 1))],
    [sg.Text("Downloading Speed: "), sg.Text("N/A", key="speedField", size=(30, 1))],
    [sg.Text(key='isCompletedField', size=(15, 1))]
]
layout = [[sg.Column(col)], [sg.Button("Download", size=(30, 40))]]
window = sg.Window("Download Manager", layout=layout, size=(500, 250))


def checkUrlValid(url):
    result = True if validators.url(url) else False
    if not result:
        sg.Popup("Url is not valid.")
    return result

def errorPopup(err):
    sg.Popup(err)


def clearInputFields():
    window['urlInput'].Update("")
    window['nameInput'].Update("")


def createFilename(name, httpContentType):
    fileExtension = mimetypes.guess_extension(httpContentType)
    if httpContentType == "application/x-zip-compressed":
        fileExtension = "zip"
    return f"{name}.{fileExtension}"


def downloadFile(url, name):
    try:
        start = time.perf_counter()
        response = requests.get(url, stream=True)
        response.raise_for_status()
        contentLength = int(response.headers['content-length'])
        totalSize = round(contentLength / 1024 / 1024, 2)
        name = createFilename(name, response.headers['Content-Type'])
        downloaded = 0
        with open(name, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
                downloaded += len(chunk)
                window['progressField'].update(f"{round(downloaded / 1024 / 1024, 2)} / {totalSize} mb")
                window['speedField'].update(f"{round(downloaded // (time.perf_counter() - start) / 100000, 2)} Mbps")
        clearInputFields()
    except requests.HTTPError as exception:
        print(exception)
        errorPopup(exception)
    except requests.TooManyRedirects as exception:
        errorPopup(exception)
        print(exception)
    except requests.Timeout as exception:
        errorPopup(exception)
        print(exception)
    except requests.ConnectionError as exception:
        errorPopup(exception)
        print(exception)


while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == "Download":
        url = values["urlInput"]
        name = values["nameInput"]
        if url and name and checkUrlValid(url):
            thread = threading.Thread(target=downloadFile, args=(url, name))
            thread.start()
        else:
            sg.Popup("Please specify required parameters", title="Error")

window.close()
