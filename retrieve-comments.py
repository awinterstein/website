#!/usr/bin/env python3

from glob import glob
from urllib.request import urlopen
import argparse
import json
import re
import tomllib
import os.path as path
from dateutil import parser as datetime_parser
from babel.dates import format_date, format_time


HEADER = "+++\nrender=false\n+++\n\n"


def get_blog_entry_files(path, exclude_translations):
    """
    Returns a list of all markdown blog entry filenames from the given directory.

    The index files are always excluded from this list and it can optionally be
    requested with the exclude_translations parameter, to only return the files
    of the default language, but exclude all translation files.
    """
    translation_pattern = re.compile(".*\\.[a-z]{2}\\.md$")
    files = []

    for file in glob(f'{path}/*.md'):
        file = file.replace(f'{path}/', '')

        if not file.startswith('_index') and (not exclude_translations or not translation_pattern.match(file)):
            files.append(file)

    return files


def get_blog_entry_comments_config(path, exclude_translations):
    """
    Returns a dictionary with the Mastodon comments configuration from each
    blog entry file from the given path.

    It can optionally be requested with the exclude_translations parameter, to
    only return the configuration from the files of the default language.
    """
    files_config = {}

    for file in get_blog_entry_files(blog_path, exclude_translations):
        with open(f'{blog_path}/{file}') as f:
            config_part = f.read().split('+++\n')[1]
            data = tomllib.loads(config_part)

            if 'extra' in data and 'comments' in data['extra']:
                files_config[file] = data

    return files_config


def create_empty_comment_files(blog_comments_path, files_comments_config):
    """
    Creates the markdown files for the comments of each blog entry.

    There are no comments in the files, only the header is written. Existing
    files are not overwritten.
    """
    for file in files_comments_config:
        comments_file = f'{blog_comments_path}/{file}'
        if not path.isfile(comments_file):
            with open(comments_file, "x") as f:
                f.write(HEADER)


def get_display_name_without_emojis(comment):
    """
    Returns the display name from the given comment dict, but with all emojis
    removed from the name.
    """
    name = comment['account']['display_name']
    for emoji in comment['account']['emojis']:
        name = name.replace(f":{emoji['shortcode']}:", "")
    return name


def create_markdown_entry(comment, locale):
    """
    Returns the string for the macro instance of the comment.

    The macro is defined in templates/shortcodes/comment.html. For now, only
    the date and time are translated according to the given locale.
    """
    connecting_word = {'en': 'at', 'de': 'um'}

    level = 1 if comment['in_reply_to_id'] == str(config['id']) else 2
    datetime = datetime_parser.parse(comment['created_at'])
    date = format_date(datetime, format='long', locale=locale)
    time = format_time(datetime, 'H:mm', locale=locale)
    return f'{{% comment(user_url="{comment['account']['url']}", comment_url="{comment['url']}", fullname="{get_display_name_without_emojis(comment)}", ' \
        f'datetime="{date} {connecting_word[locale]} {time}", avatar="{comment['account']['avatar_static']}", favorites={int(comment['favourites_count'])}, level={level}) %}}' \
        f'{comment['content']}{{% end %}}'


blog_path = 'content/blog' # path where the markdown files of the blog entries are stored
blog_comments_path = 'content/blog-comments' # path where the markdown files for the blog comments should be written

parser = argparse.ArgumentParser(
    prog='Retrieve Comments',
    description='Retrieves comments from Mastodon and creates corresponding markdown files')
parser.add_argument('--create-empty', action='store_true', help='Only create the missing empty comment files')
args = parser.parse_args()


# create the markdown files for the comments of each blog entry (without comments)
if args.create_empty:
    files_comments_config = get_blog_entry_comments_config(
        blog_path, exclude_translations=False)
    create_empty_comment_files(
        blog_comments_path, files_comments_config)

# retrieve the comments from Mastodon and write them to the markdown files
else:
    files_comments_config = get_blog_entry_comments_config(
        blog_path, exclude_translations=True)

    for file, data in files_comments_config.items():
        config = data['extra']['comments']

        # retrieve JSON from the Mastodon API
        url = f'https://{config['host']
                         }/api/v1/statuses/{config['id']}/context'
        response = json.loads(urlopen(url).read())

        # write the English comment files
        with open(f'{blog_comments_path}/{file}', "w") as f:
            f.write(HEADER)
            for comment in (response['descendants']):
                f.write(create_markdown_entry(comment, locale='en'))

        # write the German comment files
        file_german = file.replace('.md', '.de.md')
        with open(f'{blog_comments_path}/{file_german}', "w") as f:
            f.write(HEADER)
            for comment in (response['descendants']):
                f.write(create_markdown_entry(comment, locale='de'))
