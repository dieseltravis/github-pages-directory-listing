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

NOW = dt.datetime.now(dt.timezone.utc)
TEMPLATE_FOLDER = "/src/template/"
TEMPLATE_RSS_FOLDER = "/src/template/rss/"
TEMPLATE_ATOM_FOLDER = "/src/template/atom/"
SHORT_DT_FORMAT = '%Y-%m-%d'
LONG_DT_FORMAT = '%Y-%m-%d %H:%M:%S'
RSS_DT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
BUILD_DATE = NOW.strftime(LONG_DT_FORMAT)
BUILD_DATE_RSS = NOW.strftime(RSS_DT_FORMAT)
BUILD_DATE_ATOM = NOW.isoformat()
RX_FILENAME = r'[a-z0-9-]+\.[a-z]+$'
TRUE_VALS = ['true', '1', 't', 'y', 'yes', 'ok']

def main():
    """
    main function
    """
    cname = "localhost"
    try:
        cname_path = os.path.join('.', 'CNAME')
        with open(cname_path, 'r', encoding="utf-8") as cname_file:
            cname = re.sub(r'\s+', '', cname_file.read())
    except OSError:
        print("Cannot find CNAME file at '" + cname_path + "'")
    url_base = "https://" + cname + "/"

    folder = ""
    file_dates = {}
    folder_dates = {}
    do_rss, do_atom, folder = init_params(file_dates, folder_dates)
    gen_html(do_rss, do_atom, folder, file_dates, folder_dates)                
    gen_rss(do_rss, url_base, folder, file_dates)
    gen_atom(do_atom, url_base, folder, file_dates)

def gen_atom(do_atom, url_base, folder, file_dates):
    """
    generate Atom XML files
    """
    if do_atom:
        print("do_atom is true")
        atom_row = ""
        with open(TEMPLATE_ATOM_FOLDER + "row.html", "r", encoding="utf-8") as file:
            atom_row = file.read()
        for dirname, dirnames, filenames in os.walk('.'):
            print(dirnames)
            if 'atom.xml' in filenames:
                print("atom.xml already exists, skipping...")
            else:
                print("atom.xml does not exist, generating")
                with open(os.path.join(dirname, 'atom.xml'), 'w', encoding="utf-8") as f:
                    folder_path = get_clean_file_path("/" + folder + dirname + "/").removesuffix("/")
                    # site_link is full absolute link to folder
                    site_link = url_base + folder_path.removeprefix("/")
                    # atom_link is full absolute link to atom.xml
                    atom_link = site_link + "/atom.xml"
                    
                    f.write(get_atom_template_head(folder_path, atom_link, site_link, BUILD_DATE_ATOM, url_base))
                    f.write("\n")
                    # sort filenames alphabetically
                    filenames.sort()
                    # TODO: it would be nice to sort by date, recent on top
                    for filename in filenames:
                        # skip generated HTML files
                        if not filename.endswith("index.html") and not filename.endswith("rss.xml"):
                            path = (dirname == '.' and filename or dirname + '/' + filename)
                            key_name = get_clean_file_path(folder + path)
                            fulldate = file_dates[key_name]
                            ext = filename.split(".")[-1]
                            date_val = dt.datetime.fromisoformat(fulldate)
                            filepubdate = date_val.isoformat()
                            shortdate = date_val.strftime(SHORT_DT_FORMAT)
                            # filelink should be full absolute
                            filelink = url_base + key_name
                            f.write(
                                atom_row.replace("{{filelink}}", filelink)
                                    .replace("{{filename}}", filename)
                                    .replace("{{filepubdate}}", filepubdate)
                                    .replace("{{filedate}}", shortdate)
                                    .replace("{{bytes}}", str(os.path.getsize(path)))
                                    .replace("{{size}}", get_file_size(path))
                                    .replace("{{foldername}}", folder_path)
                                    .replace("{{sitelink}}", site_link)
                                    .replace("{{ext}}", ext)
                            )
                    f.write("\n")
                    f.write(get_atom_template_foot())

def gen_rss(do_rss, url_base, folder, file_dates):
    """
    generate RSS XML files
    """
    if do_rss:
        print("do_rss is true")
        rss_row = ""
        with open(TEMPLATE_RSS_FOLDER + "row.html", "r", encoding="utf-8") as file:
            rss_row = file.read()
        for dirname, dirnames, filenames in os.walk('.'):
            print(dirnames)
            if 'rss.xml' in filenames:
                print("rss.xml already exists, skipping...")
            else:
                print("rss.xml does not exist, generating")
                with open(os.path.join(dirname, 'rss.xml'), 'w', encoding="utf-8") as f:
                    folder_path = get_clean_file_path("/" + folder + dirname + "/").removesuffix("/")
                    # site_link is full absolute link to folder
                    site_link = url_base + folder_path.removeprefix("/")
                    # rss_link is full absolute link to rss.xml
                    rss_link = site_link + "/rss.xml"
                    
                    f.write(get_rss_template_head(folder_path, rss_link, site_link, BUILD_DATE_RSS))
                    f.write("\n")
                    # sort filenames alphabetically
                    filenames.sort()
                    # TODO: it would be nice to sort by date, recent on top
                    for filename in filenames:
                        # skip generated HTML files
                        if not filename.endswith("index.html"):
                            path = (dirname == '.' and filename or dirname + '/' + filename)
                            key_name = get_clean_file_path(folder + path)
                            fulldate = file_dates[key_name]
                            ext = filename.split(".")[-1]
                            date_val = dt.datetime.fromisoformat(fulldate)
                            filepubdate = date_val.strftime(RSS_DT_FORMAT)
                            shortdate = date_val.strftime(SHORT_DT_FORMAT)
                            filemime = get_mime_from_filename(filename)
                            # filelink should be full absolute
                            filelink = url_base + key_name
                            f.write(
                                rss_row.replace("{{filelink}}", filelink)
                                    .replace("{{filename}}", filename)
                                    .replace("{{filepubdate}}", filepubdate)
                                    .replace("{{filedate}}", shortdate)
                                    .replace("{{bytes}}", str(os.path.getsize(path)))
                                    .replace("{{size}}", get_file_size(path))
                                    .replace("{{filemime}}", filemime)
                                    .replace("{{ext}}", ext)
                            )
                    f.write("\n")
                    f.write(get_rss_template_foot())

def gen_html(do_rss, do_atom, folder, file_dates, folder_dates):
    """
    generate index HTML files
    """
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
                folder_path = get_clean_file_path("/" + folder + dirname + "/").removesuffix("/")
                f.write("\n".join([
                    get_template_head(folder_path, do_rss, do_atom),
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

                f.write("\n")
                f.write(get_template_foot(folder_path, do_rss, do_atom))

def init_params(file_dates, folder_dates):
    """
    init params passed in
    """
    do_rss = False
    do_atom = False
    if len(sys.argv) > 1:
        folder = sys.argv[1]
        print("changing directory to " + folder)
        # add error handling to chdir
        try:
            os.chdir(folder)
        except OSError:
            print("Cannot change the current working directory")
            sys.exit()
        if len(sys.argv) > 2:
            parse_file_dates(file_dates, folder_dates)
        else:
            print("no FILE_DATES specified")
            sys.exit()
        if len(sys.argv) > 3:
            do_rss_input = sys.argv[3]
            print("parsing do_rss " + do_rss_input)
            do_rss = do_rss_input.lower() in TRUE_VALS
        if len(sys.argv) > 4:
            do_atom_input = sys.argv[4]
            print("parsing do_atom " + do_atom_input)
            do_atom = do_atom_input.lower() in TRUE_VALS
    else:
        print("no directory specified")
        sys.exit()
    return do_rss,do_atom,folder

def parse_file_dates(file_dates, folder_dates):
    """
    parse file dates param
    """
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
            print("bad format of FILE_DATES item:" + line)
    print("file_dates loaded: " + str(len(file_dates)))
    print("folder_dates loaded: " + str(len(folder_dates)))

def get_clean_file_path(path):
    """
    get file path without dots or doubled slashes
    """
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

def get_template_head(foldername, do_rss, do_atom):
    """
    get template head
    """
    foldername = get_normalized_folder(foldername)
    with open(TEMPLATE_FOLDER + "head.html", "r", encoding="utf-8") as file:
        head = file.read()
    head = head.replace("{{foldername}}", foldername)
    if do_rss:
        head = head.replace("{{rss}}", "<link rel='alternate' type='application/rss+xml' title='RSS feed for " + foldername + "' href='rss.xml' />")
        head = head.replace("{{rsslink}}", "<a rel='alternate' type='application/rss+xml' title='RSS feed for " + foldername + "' href='rss.xml' class='rss'><img src='/i/rss.svg' alt='RSS icon' width='16' height='16' /></a>")
    else:
        head = head.replace("{{rss}}", "").replace("{{rsslink}}", "")
    if do_atom:
        head = head.replace("{{atom}}", "<link rel='alternate' type='application/atom+xml' title='Atom feed for " + foldername + "' href='atom.xml' />")
        head = head.replace("{{atomlink}}", "<a rel='alternate' type='application/atom+xml' title='Atom feed for " + foldername + "' href='atom.xml' class='atom'><img src='/i/atom.svg' alt='ATOM icon' width='16' height='16' /></a>")
    else:
        head = head.replace("{{atom}}", "").replace("{{atomlink}}", "")
    return head

def get_template_foot(foldername, do_rss, do_atom):
    """
    get template foot
    """
    foldername = get_normalized_folder(foldername)
    with open(TEMPLATE_FOLDER + "foot.html", "r", encoding="utf-8") as file:
        foot = file.read()
    foot = foot.replace("{{buildtime}}", BUILD_DATE)
    if do_rss:
        foot = foot.replace("{{rsslink}}", "<a rel='alternate' type='application/rss+xml' title='RSS feed for " + foldername + "' href='rss.xml' class='rss'><img src='/i/rss.svg' alt='RSS icon' width='16' height='16' /></a>")
    else:
        foot = foot.replace("{{rsslink}}", "")
    if do_atom:
        foot = foot.replace("{{atomlink}}", "<a rel='alternate' type='application/atom+xml' title='Atom feed for " + foldername + "' href='atom.xml' class='atom'><img src='/i/atom.svg' alt='ATOM icon' width='16' height='16' /></a>")
    else:
        foot = foot.replace("{{atomlink}}", "")
    return foot

def get_rss_template_head(foldername, rsslink, sitelink, lastdate):
    """
    get RSS template head
    """
    foldername = get_normalized_folder(foldername)
    with open(TEMPLATE_RSS_FOLDER + "head.html", "r", encoding="utf-8") as file:
        head = file.read()
    head = head.replace("{{foldername}}", foldername).replace("{{rsslink}}", rsslink).replace("{{sitelink}}", sitelink).replace("{{lastdate}}", lastdate)
    return head

def get_rss_template_foot():
    """
    get RSS template foot
    """
    with open(TEMPLATE_RSS_FOLDER + "foot.html", "r", encoding="utf-8") as file:
        foot = file.read()
    return foot

def get_atom_template_head(foldername, atomlink, sitelink, lastdate, rootlink):
    """
    get Atom template head
    """
    foldername = get_normalized_folder(foldername)
    with open(TEMPLATE_ATOM_FOLDER + "head.html", "r", encoding="utf-8") as file:
        head = file.read()
    head = head.replace("{{foldername}}", foldername).replace("{{atomlink}}", atomlink).replace("{{sitelink}}", sitelink).replace("{{lastdate}}", lastdate).replace("{{rootlink}}", rootlink)
    return head

def get_atom_template_foot():
    """
    get Atom template foot
    """
    with open(TEMPLATE_ATOM_FOLDER + "foot.html", "r", encoding="utf-8") as file:
        foot = file.read()
    return foot

def get_normalized_folder(foldername):
    """
    remove the dot (.) at the beginning of foldername
    """
    if foldername.startswith('.'):
        if not foldername.startswith('/', 1):
            return get_normalized_folder('/' + foldername[1:])
        return get_normalized_folder(foldername[1:])
    return foldername

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

def get_mime_from_filename(filename):
    """
    get MIME from filename
    """
    extension = "." + filename.split(".")[-1]
    for m in data:
        if extension in m["extension"]:
            return m["mime"]
    return "application/octet"

if __name__ == "__main__":
    main()
