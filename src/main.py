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

ICON_FOLDER = "/src/w98/"
with open('/src/w98.json', encoding="utf-8") as json_file:
    data = json.load(json_file)

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
                    if len(pair) > 1:
                        file_dates[pair[0]] = pair[1]
                        folder_key = re.sub(r'[a-z0-9-]+\.[a-z]+$', '', pair[0])
                        print(folder_key)
                        this_date = dt.datetime.fromisoformat(pair[1])
                        if not (folder_key in folder_dates) or folder_dates[folder_key] < this_date:
                            folder_dates[folder_key] = this_date
            print("file_dates loaded: " + str(len(file_dates)))
        else:
            print("no FILE_DATES specified")
            sys.exit()
    else:
        print("no directory specified")
        sys.exit()

    row = ""
    with open("/src/template/row.html", "r", encoding="utf-8") as file:
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
                    get_template_head(("/" + folder + dirname + "/").replace("/.", "/").replace("./", "/").replace("//", "/").removesuffix("/")),
                    row.replace("{{icon}}", homeicon)
                        .replace("{{type}}", "home")
                        .replace("{{href}}", "../")
                        .replace("{{filename}}", "..")
                        .replace("{{sortdate}}", "-")
                        .replace("{{fulldate}}", dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        .replace("{{shortdate}}", "")
                        .replace("{{bytes}}", "0")
                        .replace("{{size}}", "") if dirname != "." else "",
                ]))
                # sort dirnames alphabetically
                dirnames.sort()
                for subdirname in dirnames:
                    key_name = (folder + subdirname + "/").replace("/.", "/").replace("./", "/").replace("//", "/")
                    folder_date = folder_dates[key_name]
                    sort_folder_date = folder_date.strftime('%Y-%m-%d %H:%M:%S')
                    short_folder_date = folder_date.strftime('%Y-%m-%d')

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
                    path = (dirname == '.' and filename or dirname +
                            '/' + filename)
                    key_name = (folder + path).replace("/.", "/").replace("./", "/").replace("//", "/")
                    fulldate = file_dates[key_name]
                    ext = filename.split(".")[-1]
                    shortdate = dt.datetime.fromisoformat(fulldate).strftime('%Y-%m-%d')
                    f.write(
                        row.replace("{{icon}}", get_icon_base64(filename))
                            .replace("{{type}}", ext)
                            .replace("{{href}}", filename)
                            .replace("{{filename}}", filename)
                            .replace("{{sortdate}}", fulldate)
                            .replace("{{fulldate}}", fulldate)
                            .replace("{{shortdate}}", shortdate)
                            .replace("{{bytes}}", str(os.path.getsize(path)))
                            .replace("{{size}}", get_file_size(path))
                    )

                f.write("\n".join([
                    get_template_foot(),
                ]))


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


def get_file_created_time(filepath):
    """
    get file modified time
    """
    return dt.datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
    
def get_file_modified_time(filepath):
    """
    get file modified time
    """
    return dt.datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')

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

    with open("/src/template/head.html", "r", encoding="utf-8") as file:
        head = file.read()
    head = head.replace("{{foldername}}", foldername)
    return head


def get_template_foot():
    """
    get template foot
    """
    with open("/src/template/foot.html", "r", encoding="utf-8") as file:
        foot = file.read()
    foot = foot.replace("{{buildtime}}", dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
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
