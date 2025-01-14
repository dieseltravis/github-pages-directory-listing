#!/usr/local/bin/python3
"""
use os package to iterate through files in a directory
"""
import os
import sys
#import git
#from git.objects.commit import Commit
#import subprocess
import json
import base64
import datetime as dt

with open('/src/icons.json', encoding="utf-8") as json_file:
    data = json.load(json_file)


def main():
    """
    main function
    """
    gif_dates = {}
    gif_dates_input = ""
    if len(sys.argv) > 1:
        print("changing directory to " + sys.argv[1])
        # add error handling to chdir
        try:
            os.chdir(sys.argv[1])
        except OSError:
            print("Cannot change the current working Directory")
            sys.exit()
        if len(sys.argv) > 2:
            gif_dates_input = sys.argv[2]
            for line in gif_dates_input.split("!")
                if len(line) > 1:
                    pair = line.split("|")
                    if len(pair) > 1;
                        gif_dates[pair[0]] = pair[1]
        else:
            print("no GIF_DATES specified")
            sys.exit()
    else:
        print("no directory specified")
        sys.exit()

    with open("/src/template/row.html", "r", encoding="utf-8") as file:
        row = file.read()
    homeicon = get_icon_base64("o.folder-home")
    foldericon = get_icon_base64("o.folder")

    #submissionDate_fileName = {}
    #dir_path = os.path.dirname(os.path.realpath(__file__))
    #repo = git.Repo(dir_path)
    #tree = repo.tree()
    #for blob in tree.trees[1]:
    #    commit = next(repo.iter_commits(paths=blob.path, max_count=1))
    #    date = str(get_date(commit.committed_date))[:10]
    #    submissionDate_fileName[blob.name] = date
    
    for dirname, dirnames, filenames in os.walk('.'):
        if 'index.html' in filenames:
            print("index.html already exists, skipping...")
        else:
            print("index.html does not exist, generating")
            with open(os.path.join(dirname, 'index.html'), 'w', encoding="utf-8") as f:
                f.write("\n".join([
                    get_template_head(dirname),
                    row.replace("{{icon}}", homeicon).replace("{{href}}", "../").replace("{{filename}}", "../").replace("{{date}}", "").replace("{{bytes}}", "0").replace("{{size}}", "") if dirname != "." else "",
                ]))
                # sort dirnames alphabetically
                dirnames.sort()
                for subdirname in dirnames:
                    f.write(
                        row.replace("{{icon}}", foldericon).replace("{{href}}", subdirname).replace("{{filename}}", subdirname).replace("{{date}}", "").replace("{{bytes}}", "0").replace("{{size}}", "")
                    )
                # sort filenames alphabetically
                filenames.sort()
                for filename in filenames:
                    path = (dirname == '.' and filename or dirname +
                            '/' + filename)
                    f.write(
                        row.replace("{{icon}}", get_icon_base64(filename)).replace("{{href}}", filename).replace("{{filename}}", filename).replace("{{date}}", gif_dates[path]).replace("{{bytes}}", str(os.path.getsize(path))).replace("{{size}}", get_file_size(path))
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
    # return time.ctime(os.path.getmtime(filepath)).strftime('%X %x')

#def get_date(epoch_time):
#    return datetime.fromtimestamp(epoch_time)
    
#def get_file_last_commit_date(filepath):    
#    try:
#        # Use `git log` to get the last commit date for the file
#        result = subprocess.run(
#            ["git", "log", "-1", "--format=%ci", "--", filepath],
#            stdout=subprocess.PIPE,
#            stderr=subprocess.PIPE,
#            text=True,
#            check=True
#        )
#        # The result will be in the format: YYYY-MM-DD HH:MM:SS +TZ
#        return result.stdout.strip()
#    except subprocess.CalledProcessError as e:
#        print(f"Error getting file date: {e.stderr.strip()}")
#        return ""

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
    with open("/src/png/" + get_icon_from_filename(filename), "rb") as file:
        return "data:image/png;base64, " + base64.b64encode(file.read()).decode('ascii')


def get_icon_from_filename(filename):
    """
    get icon from filename
    """
    extension = "." + filename.split(".")[-1]
    # extension = "." + extension
    # print(extension)
    for i in data:
        if extension in i["extension"]:
            # print(i["icon"])
            return i["icon"] + ".png"
    # print("no icon found")
    return "unknown.png"


if __name__ == "__main__":
    main()
    # get_icon_from_filename("test.txppt")
