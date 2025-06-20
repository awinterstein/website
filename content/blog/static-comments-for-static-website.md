+++
title = "Comments for Static Website (with Mastodon)"
description = "How I added a static comment feature to my static website."
authors = ["Adrian Winterstein"]
date = "2025-02-28"

[taxonomies]
blog-tags=["Web", "Zola"]

[extra]
comments.host = "mastodon.social"
comments.username = "awinterstein"
comments.id = 114081713837118160
+++

When I created this website and blog as a static website with [Zola](https://www.getzola.org/), I wondered how I could add a comment feature.

A quick search revealed the post [Adding comments to your static blog with Mastodon](https://carlschwan.eu/2020/12/29/adding-comments-to-your-static-blog-with-mastodon/) from Carl Schwan, in which he explains how he shows responds to his Mastodon posts as comments to his blog. This was already very close to what I wanted to achieve, however, I would prefer a solution that works without the need to dynamically load the comments via JavaScript. Hence, based on his solution I created a completely static integration of Mastodon responses as comments into my website.

## Prepare Static Website for Comments

The content of the static website is provided in Markdown files, which means that there is a Markdown file for each blog post. Comments could be directly added there as well, however, for a cleaner separation of blog content and comments, I decided to use a separate Markdown file for the comments for each blog post. For this post, which is located at `content/blog/static-comments-for-static-website.md`, the comments would be added to the file `content/blog-comments/static-comments-for-static-website.md`.

As long as the comments file has the same filename as the Markdown file of the blog post, the comments can be included for the blog post, by adding the following to the blog page template:

```jinja2
{#- Show comments and link to Mastodon post, if the comments variables are set for the page. -#}
{%- if page.extra.comments.host and page.extra.comments.username and page.extra.comments.id -%}

  {#- Generate comment filename from current filename (same name different path) and load its content. -#}
  {%- set comments_file = page.relative_path | split(pat="/") | last -%}
  {%- set comments = get_page(path="blog-comments/" ~ comments_file) -%}

  {#- Show comments, if there are any in the comments file. -#}
  {%- if comments.content -%}
    <h2>Comments</h2>
    {{ comments.content | safe }}
  {%- endif -%}

  {#- Show link to the corresponding Mastodon post. -#}
  <a href="https://{{ page.extra.comments.host }}/@{{ page.extra.comments.username }}/{{ page.extra.comments.id }}" target="_blank">Comment on Mastodon</a>

{%- endif -%}
```

For the comments itself, I added a [shortcode](https://www.getzola.org/documentation/content/shortcodes/), so that the presentation is separated from the content:

```html
<div class="comment flex mt-2 mb-4 {% if level > 1 %}ml-8{%endif %}">
    <a href="{{ user_url }}" target="_blank" rel="external nofollow"><img src="{{ avatar }}" class="h-12 w-12 object-cover rounded-full mr-2"></a>
    <div>
        <div>
            <a href="{{ user_url }}" target="_blank" rel="external nofollow" class="mr-12">{{ fullname }}</a>
        </div>
        <a href="{{ comment_url }}" target="_blank" rel="external nofollow" class="text-sm">{{ datetime }}</a>
        <div class="mt-2">
            {{ body | safe }}
        </div>
        {% if favorites > 0 %}
        <a href="{{ comment_url }}/favourites" target="_blank"><div class="text-sm">{{ content::icon(id="heart") }}{{ favorites }}</div>
        {% endif %}
    </div>
</div>
```

The shortcode can be instantiated like this in the comments Markdown file:

```jinja
{%/* comment(user_url="https://mastodon.social/@awinterstein",
    comment_url="https://mastodon.social/@awinterstein/114081720861078028",
    fullname="Adrian Winterstein",
    datetime="February 28, 2025 at 13:21",
    avatar="https://files.mastodon.social/accounts/avatars/113/945/630/736/175/025/original/08b18b1267a1fe54.jpg",
    favorites=1, level=1) */%}
This comment is just a test to show the Mastodon responses feature in my blog.
{%/* end */%}
```

Which would lead to the following rendering:

{% comment(user_url="https://mastodon.social/@awinterstein",
   comment_url="https://mastodon.social/@awinterstein/114081720861078028",
   fullname="Adrian Winterstein",
   datetime="February 28, 2025 at 13:21",
   avatar="https://files.mastodon.social/accounts/avatars/113/945/630/736/175/025/original/08b18b1267a1fe54.jpg",
   favorites=1, level=1) %}
<p>This comment is just a test to show the Mastodon responses feature in my blog.</p>
{% end %}

With the templates and comment files being prepared, it was then possible to create a script to retrieve the comments from Mastodon and fill them into the comments files.

## Retrieving Comments from Mastodon

As described by Carl Schwan, there is a simple API available on Mastodon, to retrieve all replies to a given post. I created a small Python script that iterates through all blog entries, retrieves the Mastodon post IDs from the entries and checks the Mastodon API for the responses to this post.

```python
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


# the TOML header of the Markdown files (as defined for Zola)
HEADER = "+++\nrender=false\n+++\n\n"

# path where the markdown files of the blog entries are stored
BLOG_PATH = 'content/blog'

# path where the markdown files for the blog comments should be written
BLOG_COMMENTS_PATH = 'content/blog-comments'

# the default language of the website as defined in the config.toml
DEFAULT_LANGUAGE = "en"

# additional languages of the website as defined in the config.toml
ADDITIONAL_LANGUAGES = ["de"]


def get_blog_entry_files(path, exclude_translations):
    """
    Returns a list of all markdown blog entry filenames from the given directory.

    The index files are always excluded from this list and it can optionally be
    requested with the exclude_translations parameter, to only return the files
    of the default language, but exclude all translation files.
    """

    # pattern for markdown file names in additional languages that contain a language code (e.g, blog-entry.de.md)
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

    for file in get_blog_entry_files(BLOG_PATH, exclude_translations):
        with open(f'{BLOG_PATH}/{file}') as f:
            config_part = f.read().split('+++\n')[1]
            data = tomllib.loads(config_part)

            if 'extra' in data and 'comments' in data['extra']:
                files_config[file] = data

    return files_config


def create_empty_comment_files(BLOG_COMMENTS_PATH, files_comments_config):
    """
    Creates the markdown files for the comments of each blog entry.

    There are no comments in the files, only the header is written. Existing
    files are not overwritten.
    """
    for file in files_comments_config:
        comments_file = f'{BLOG_COMMENTS_PATH}/{file}'
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
        f'{comment['content']}{{% end %}}'


if __name__ == "__main__":
    # argument handling to allow for the parameter for creating the missing files
    parser = argparse.ArgumentParser(
        prog='Retrieve Comments',
        description='Retrieves comments from Mastodon and creates corresponding markdown files')
    parser.add_argument('--create-empty', action='store_true',
                        help='Only create the missing empty comment files')
    args = parser.parse_args()

    # create the markdown files for the comments of each blog entry (without comments)
    if args.create_empty:
        files_comments_config = get_blog_entry_comments_config(
            BLOG_PATH, exclude_translations=False)
        create_empty_comment_files(
            BLOG_COMMENTS_PATH, files_comments_config)

    # retrieve the comments from Mastodon and write them to the markdown files
    else:
        files_comments_config = get_blog_entry_comments_config(
            BLOG_PATH, exclude_translations=True)

        for file, data in files_comments_config.items():
            config = data['extra']['comments']

            # retrieve JSON from the Mastodon API
            url = f'https://{config['host']}/api/v1/statuses/{config['id']}/context'
            response = json.loads(urlopen(url).read())

            # write the default language comment files
            with open(f'{BLOG_COMMENTS_PATH}/{file}', "w") as f:
                f.write(HEADER)
                for comment in (response['descendants']):
                    f.write(create_markdown_entry(comment, locale=DEFAULT_LANGUAGE))

            # write the additional language comment files
            for language in ADDITIONAL_LANGUAGES:
                file_with_language = file.replace('.md', f'.{language}.md')
                with open(f'{BLOG_COMMENTS_PATH}/{file_with_language}', "w") as f:
                    f.write(HEADER)
                    for comment in (response['descendants']):
                        f.write(create_markdown_entry(comment, locale=language))
```

In addition to retrieving the responses, this script also provides the functionality to create the empty comment files for each blog entry. This is needed, because the used static site generator Zola does not support checking file existence before including a file. Hence, the comment files that are included as described before, all need to exist when building the site.

## Integration with CI Pipelines

I didn't want to run the script manually, hence I added a Github workflow to regularly retrieve the responses from Mastodon and notify me by creating a pull-request as soon as there are any new, changed or deleted comments. The workflow calls the `retrieve-comments.py` script and, if there are any changes in the files afterwards, it creates a new branch and a pull-request with those changes.

```yaml
name: Add Comments

on:
  schedule:
  - cron: '30 20 * * *'
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write

jobs:
  comments:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          submodules: recursive
      - name: Retrieve Comments
        run: ./retrieve-comments.py
      - name: Create Pull-Request
        run: |
          if [ ! -z "$(git status --untracked-files=no --porcelain)" ]; then
            git config --local user.email "adrian@winterstein.biz"
            git config --local user.name  "Adrian Winterstein"

            # checkout a branch, commit the comment changes and push the branch
            git checkout -b "feature/comments-adaption"
            git commit -a -m "Changed blog comments according to changes on Mastodon."
            git push origin $(git branch --show-current) --force-with-lease -f

            # create pull-request, if it dows not exist yet
            if [ -z $(gh pr list --search "head:feature/comments-adaption" ) ]; then
              gh pr create -B main -l comments -a awinterstein \
                -t "Changed blog comments according to changes on Mastodon" \
                -b "This is an automatically created pull-requests due to changes of the blog comments on Mastodon."
            fi
          fi
        env:
          GH_TOKEN: ${{ secrets.ACTIONS_ACCESS_TOKEN }}
```

Running the workflow once a day should keep the load on the Mastodon server low, while still being frequent enough for a small blog, where I do not expect a lot of comments.

## Creating a Blog Post

After publishing a blog post, a corresponding post on Mastodon needs to be created then. So that readers have a place to respond on. When the Mastodon post was created, the following variables can be added to the blog post, to link the blog to the Mastodon post:

```toml
[extra]
comments.host = "mastodon.social" # my Mastodon instance
comments.username = "awinterstein" # my Mastodon username
comments.id = 114081713837118160 # the id of my Mastodon post
```

The `retrieve-comments.py` script uses those and will retrieve all replies of the Mastodon post from then on. Hence, the next pipeline execution after someone responded, will create a pull-request to integrate the comment into the static blog. If someone updates or deletes their response, this will be updated automatically as well.
