#!/usr/bin/env python

# Super Simple Site Generator in Python v1.1.1 - https://github.com/peterkaminski/supersimple
# This is free and unencumbered software released into the public domain.

import argparse
import os
import traceback
import shutil
import markdown2
import datetime
from pathlib import Path

import jinja2

# set up argparse
def init_argparse():
    parser = argparse.ArgumentParser(description='Assemble static website.')
    parser.add_argument('--site', '-s', default="site", metavar="SITE_DIR", help='directory for website output')
    parser.add_argument('--templates', '-t', default="templates", metavar="TEMPLATES_DIR", help='directory for HTML templates to process')
    parser.add_argument('--content', '-c', default="content", metavar="CONTENT_DIR", help="directory for markdown content")
    parser.add_argument('--quiet', '-q', action='store_true', help="don't print progress messages")
    return parser

# set up a Jinja2 environment
def jinja2_environment(path_to_templates):
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path_to_templates)
    )

def get_markdown_content(content_path):
    if os.path.exists(content_path):
        with open(content_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return markdown2.markdown(
                content,
                extras=['fenced-code-blocks', 'header-ids', 'tables', 'break-on-newline']
            )
    return ''

def main():
    argparser = init_argparse()
    args = argparser.parse_args()

    # remember paths
    dir_site = os.path.abspath(args.site)
    dir_templates = os.path.abspath(args.templates)
    dir_content = os.path.abspath(args.content)

    if not args.quiet:
        print(f"Directory for HTML templates to process: '{dir_templates}'")
        print(f"Directory for markdown output: '{dir_content}'")
        print(f"Directory for website output: '{dir_site}'")
        print()

    # get a Jinja2 environment
    j = jinja2_environment(dir_templates)

    # remember build time
    build_time = datetime.datetime.now(datetime.timezone.utc)
    build_time_iso = build_time.isoformat()
    build_time_human = build_time.strftime("%A, %d %B %Y, at %H:%M UTC")
    build_time_us = build_time.strftime("%A, %B %d, %Y at %H:%M UTC")

    # render the site
    try:
        for root, dirs, files in os.walk(dir_templates):
            files = [f for f in files if not f.startswith(('.', '_', '='))]
            path = root[len(dir_templates)+1:]
            output_dir = Path(dir_site) / path
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            for file in files:
                input_path = Path(root) / file
                output_path = output_dir / file
                if file.lower().endswith('.html'):
                    if not args.quiet:
                        print(f"Reading '{input_path}'")

                        markdown_file = Path(dir_content) / f"{file.replace('.html', '.md')}"
                        markdown_content = get_markdown_content(markdown_file)

                    html = j.get_template(file).render(
                        output_filename=file,
                        build_time_iso=build_time_iso,
                        build_time_human=build_time_human,
                        build_time_us=build_time_us,
                        markdown_content=markdown_content
                    )
                    output_path.write_text(html)

                    if not args.quiet:
                        print(f"Wrote '{output_path}'")
                        print()
                else:
                    shutil.copy2(input_path, output_path)
                    if not args.quiet:
                        print(f"Copied '{input_path}' to '{output_path}'")
                        print()

    except Exception as e:
        traceback.print_exc()

    if not args.quiet:
        print("Done.")

if __name__ == "__main__":
    exit(main())
