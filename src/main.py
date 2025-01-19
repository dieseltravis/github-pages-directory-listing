#!/usr/local/bin/python3
"""
use os package to iterate through files in a directory
"""
import os
import re
import sys
import json
import base64
import datetime as dt

# TODO: set these up as params?
ICON_FOLDER = "/src/w98/"
with open('/src/w98.json', encoding="utf-8") as json_file:
    data = json.load(json_file)

TEMPLATE_FOLDER = "/src/template/"
SHORT_DT_FORMAT = '%Y-%m-%d'
LONG_DT_FORMAT = '%Y-%m-%d %H:%M:%S'
BUILD_DATE = dt.datetime.now().strftime(LONG_DT_FORMAT)
RX_FILENAME = r'[a-z0-9-]+\.[a-z]+$'

def main():
    """
    main function
    """
    folder = ""
    file_dates = {}
    folder_dates = {}
    file_dates_input = ""
    
    if len(sys.argv) > 1:
        folder = sys.argv[1]
        print("changing directory to " + folder)
        # add error handling to chdir
        try:
            os.chdir(folder)
        except OSError:
            print("Cannot change the current working Directory")
            sys.exit()
        if len(sys.argv) > 2:
            file_dates_input = sys.argv[2]
            print("parsing " + file_dates_input)
            for line in file_dates_input.split("!"):
                if len(line) > 1:
                    print("pair: " + line)
                    pair = line.split("|")
                    if len(pair) == 2:
                        file_dates[pair[0]] = pair[1]
                        # get just folder path
                        folder_key = re.sub(RX_FILENAME, '', pair[0])
                        print(folder_key)
                        this_date = dt.datetime.fromisoformat(pair[1])
                        # use latest file date for folder date
                        if not (folder_key in folder_dates) or folder_dates[folder_key] < this_date:
                            folder_dates[folder_key] = this_date
                    else:
                        print("bad format of file|date:" + line)
                else:
                    print("bad format of FILE_DATES item:" + file_dates_input)
            print("file_dates loaded: " + str(len(file_dates)))
            print("folder_dates loaded: " + str(len(folder_dates)))
        else:
            print("no FILE_DATES specified")
            sys.exit()
    else:
        print("no directory specified")
        sys.exit()

    row = ""
    with open(TEMPLATE_FOLDER + "row.html", "r", encoding="utf-8") as file:
        row = file.read()
    homeicon = get_icon_base64("o.folder-home")
    foldericon = get_icon_base64("o.folder")
    
    for dirname, dirnames, filenames in os.walk('.'):
        if 'index.html' in filenames:
            print("index.html already exists, skipping...")
        else:
            print("index.html does not exist, generating")
            with open(os.path.join(dirname, 'index.html'), 'w', encoding="utf-8") as f:
                f.write("\n".join([
                    get_template_head(get_clean_file_path("/" + folder + dirname + "/").removesuffix("/")),
                    row.replace("{{icon}}", homeicon)
                        .replace("{{type}}", "home")
                        .replace("{{href}}", "../")
                        .replace("{{filename}}", "..")
                        .replace("{{sortdate}}", "-")
                        .replace("{{fulldate}}", BUILD_DATE)
                        .replace("{{shortdate}}", "")
                        .replace("{{bytes}}", "0")
                        .replace("{{size}}", "") if dirname != "." else "",
                ]))
                # sort dirnames alphabetically
                dirnames.sort()
                for subdirname in dirnames:
                    key_name = get_clean_file_path(folder + subdirname + "/")
                    folder_date = folder_dates[key_name]
                    sort_folder_date = folder_date.strftime(LONG_DT_FORMAT)
                    short_folder_date = folder_date.strftime(SHORT_DT_FORMAT)

                    f.write(
                        row.replace("{{icon}}", foldericon)
                            .replace("{{type}}", "folder")
                            .replace("{{href}}", subdirname)
                            .replace("{{filename}}", subdirname)
                            .replace("{{sortdate}}", "-" + sort_folder_date)
                            .replace("{{fulldate}}", sort_folder_date)
                            .replace("{{shortdate}}", short_folder_date)
                            .replace("{{bytes}}", "0")
                            .replace("{{size}}", "")
                    )
                # sort filenames alphabetically
                filenames.sort()
                for filename in filenames:
                    path = (dirname == '.' and filename or dirname + '/' + filename)
                    key_name = get_clean_file_path(folder + path)
                    fulldate = file_dates[key_name]
                    ext = filename.split(".")[-1]
                    date_val = dt.datetime.fromisoformat(fulldate)
                    longdate = date_val.strftime(LONG_DT_FORMAT)
                    shortdate = date_val.strftime(SHORT_DT_FORMAT)
                    f.write(
                        row.replace("{{icon}}", get_icon_base64(filename))
                            .replace("{{type}}", ext)
                            .replace("{{href}}", filename)
                            .replace("{{filename}}", filename)
                            .replace("{{sortdate}}", fulldate)
                            .replace("{{fulldate}}", longdate)
                            .replace("{{shortdate}}", shortdate)
                            .replace("{{bytes}}", str(os.path.getsize(path)))
                            .replace("{{size}}", get_file_size(path))
                    )

                f.write("\n".join([
                    get_template_foot(),
                ]))


def get_clean_file_path(path):
    return path.replace("/.", "/").replace("./", "/").replace("//", "/")

def get_file_size(filepath):
    """
    get file size
    """
    size = os.path.getsize(filepath)
    if size < 1024:
        return str(size) + " B"
    elif size < 1024 * 1024:
        return str(round((size / 1024), 2)) + " KB"
    elif size < 1024 * 1024 * 1024:
        return str(round((size / 1024 / 1024), 2)) + " MB"
    else:
        return str(round((size / 1024 / 1024 / 1024), 2)) + " GB"
    return str(size)

def get_template_head(foldername):
    """
    get template head
    """
    # remove the dot (.) at the beginning of foldername
    if foldername.startswith('.'):
        if not foldername.startswith('/', 1):
            return get_template_head('/' + foldername[1:])
        else:
            return get_template_head(foldername[1:])

    with open(TEMPLATE_FOLDER + "head.html", "r", encoding="utf-8") as file:
        head = file.read()
    head = head.replace("{{foldername}}", foldername)
    return head

def get_template_foot():
    """
    get template foot
    """
    with open(TEMPLATE_FOLDER + "foot.html", "r", encoding="utf-8") as file:
        foot = file.read()
    foot = foot.replace("{{buildtime}}", BUILD_DATE)
    return foot

def get_icon_base64(filename):
    """
    get icon base64
    """
    with open(ICON_FOLDER + get_icon_from_filename(filename), "rb") as file:
        return "data:image/png;base64," + base64.b64encode(file.read()).decode('ascii')

def get_icon_from_filename(filename):
    """
    get icon from filename
    """
    extension = "." + filename.split(".")[-1]
    for i in data:
        if extension in i["extension"]:
            return i["icon"] + ".png"
    return "web-file.png"

if __name__ == "__main__":
    main()
