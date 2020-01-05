"""
Copyright (c) 2018-2019 Mickaël "Kilawyn" Walter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import html
from datetime import datetime

from lib.console import Console
from lib.utils import get_by_id

class Exporter:
    """
    Utility functions to export data
    """

    @staticmethod
    def export_posts(posts, folder, tags_list=None, categories_list=None,
    users_list=None):
        """
        Exports posts as HTML to specified export folder
        param posts: the posts to export
        param folder: the export folder
        param tags_list: a list of tags to associate them with tag ids
        param categories_list: a list of categories to associate them with
        category ids
        param user_list: a list of users to associate them with author id
        """
        exported_posts = 0

        date_format = "%Y-%m-%dT%H:%M:%S-%Z"

        if not os.path.isdir(folder):
            os.makedirs(folder)
        for post in posts:
            post_file = None
            if 'slug' in post.keys():
                post_file = open(os.path.join(folder, post['slug'])+".html",
                "wt")
            else:
                post_file = open(os.path.join(folder, str(post['id']))+".html",
                "wt")

            title = "Unknown"
            if 'title' in post.keys() and 'rendered' in post['title'].keys():
                title = post['title']['rendered']

            date_gmt = "Unknown"
            if 'date_gmt' in post.keys():
                date_gmt = datetime.strptime(post['date_gmt'] +
                                             "-GMT", date_format)
            modified_gmt = "Unknown"
            if 'modified_gmt' in post.keys():
                modified_gmt = datetime.strptime(post['modified_gmt'] +
                                                 "-GMT", date_format)
            status = "Unknown"
            if 'status' in post.keys():
                status = post['status']

            post_type = "Unknown"
            if 'type' in post.keys():
                post_type = post['type']

            link = "Unknown"
            if 'link' in post.keys():
                link = html.escape(post['link'])

            comments = "Unknown"
            if 'comment_status' in post.keys():
                comments = html.escape(post['comment_status'])

            content = "Unknown"
            if 'content' in post.keys() and 'rendered' in \
                    post['content'].keys():
                content = post['content']['rendered']

            excerpt = "Unknown"
            if 'excerpt' in post.keys() and 'rendered' in \
                    post['excerpt'].keys():
                excerpt = post['excerpt']['rendered']

            author = "Unknown"
            if 'author' in post.keys() and users_list is not None:
                author_obj = get_by_id(users_list, post['author'])
                author = "%d: " % post['author']
                if author_obj is not None:
                    if 'name' in author_obj.keys():
                        author += author_obj['name']
                    if 'slug' in author_obj.keys():
                        author += "(%s)" % author_obj['slug']
                    if 'link' in author_obj.keys():
                        author += " - <a href=\"%s\">%s</a>" % \
                                  (author_obj['link'], author_obj['link'])
            elif 'author' in post.keys():
                author = str(post['author'])

            categories = "<li>Unknown</li>"
            if 'categories' in post.keys() and categories_list is not None:
                categories = ""
                for cat in post['categories']:
                    cat_obj = get_by_id(categories_list, cat)
                    categories += "<li>%d: " % cat
                    if cat_obj is not None:
                        if 'name' in cat_obj.keys():
                            categories += cat_obj['name']
                        if 'link' in cat_obj.keys():
                            categories += " - <a href=\"%s\">%s</a>" % \
                                          (html.escape(cat_obj['link']),
                                           html.escape(cat_obj['link']))
                    categories += "</li>"
            elif 'categories' in post.keys():
                categories = ""
                for cat in post['categories']:
                    categories += "<li>" + str(post['categories']) + "</li>"

            tags = "<li>Unknown</li>"
            if 'tags' in post.keys() and tags_list is not None:
                tags = ""
                for tag in post['tags']:
                    tag_obj = get_by_id(tags_list, tag)
                    tags += "<li>%d: " % tag
                    if tag_obj is not None:
                        if 'name' in tag_obj.keys():
                            tags += tag_obj['name']
                        if 'link' in tag_obj.keys():
                            tags += " - <a href=\"%s\">%s</a>" % \
                                    (html.escape(tag_obj['link']),
                                     html.escape(tag_obj['link']))
                    tags += "</li>"
            elif 'tags' in post.keys():
                tags = ""
                for cat in post['tags']:
                    tags += "<li>" + str(post['categories']) + "</li>"

            buffer = \
"""<!DOCTYPE html>
<html>
    <head>
        <title>{title}</title>
    </head>
    <body>
        <div>
            <h1>Metadata</h1>
            <ul>
                <li><strong>Date (GMT):</strong> {date_gmt}</li>
                <li><strong>Date modified (GMT):</strong> {modified_gmt}</li>
                <li><strong>Status:</strong> {status}</li>
                <li><strong>Type:</strong> {post_type}</li>
                <li><strong>Link:</strong> <a href=\"{link}\">{link}</a></li>
                <li><strong>Author:</strong> {author}</li>
                <li><strong>Comment status:</strong> {comments}</a></li>
                <li>
                    <strong>Categories:</strong>
                    <ul>
                        {categories}
                    </ul>
                </li>
                <li>
                    <strong>Tags:</strong>
                    <ul>
                        {tags}
                    </ul>
                </li>
            </ul>
        </div>
        <div>
            <h1>Excerpt</h1>
            {excerpt}
        </div>
        <div>
            <h1>{title}</h1>
            {content}
        </div>
    </body>
</html>
"""
            buffer = buffer.format(
            title=title,
            date_gmt=date_gmt.strftime("%d/%m/%Y %H:%M:%S"),
            modified_gmt=modified_gmt.strftime("%d/%m/%Y %H:%M:%S"),
            status=status,
            post_type=post_type,
            link=link,
            author=author,
            comments=comments,
            categories=categories,
            tags=tags,
            excerpt=excerpt,
            content=content
            )

            post_file.write(buffer)
            post_file.close()
            exported_posts += 1

        return exported_posts

    @staticmethod
    def export_comments(posts, orphan_comments, export_folder):
        """
        Exports comments from posts and from orphans list
        """
        exported_comments = 0
        for post in posts:
            if 'comments' in post.keys() and len(post['comments']) > 0:
                for comment in post['comments']:
                    if 'slug' in post.keys() and len(post['slug']) > 0:
                        Exporter.export_comments_helper(comment, post['slug'], export_folder)
                    else:
                        Exporter.export_comments_helper(comment, post['id'], export_folder)
                    exported_comments += 1
        for comment in orphan_comments:
            Exporter.export_comments_helper(comment, '__orphan_comments', export_folder)
            exported_comments += 1
        return exported_comments

    @staticmethod 
    def export_comments_helper(comment, post, export_folder):
        date_format = "%Y-%m-%dT%H:%M:%S-%Z"
        if not os.path.isdir(export_folder):
            os.mkdir(export_folder)
        if not os.path.isdir(os.path.join(export_folder, post)):
            os.mkdir(os.path.join(export_folder, post))
        out_file = open(os.path.join(export_folder, post, "%04d.html" % comment['id']), "wt")
        date_gmt = "Unknown"
        if 'date_gmt' in comment.keys():
            date_gmt = datetime.strptime(comment['date_gmt'] +
                                            "-GMT", date_format)
        post_link = "None"
        if '_links' in comment.keys() and 'up' in comment['_links'].keys() and len(comment['_links'].keys()) > 0 and 'href' in comment['_links']['up'][0].keys():
            post_link = html.escape(comment['_links']['up'][0]['href'])
        buffer = """
<!DOCTYPE html>
<html>
    <head>
        <title>{author}</title>
    </head>
    <body>
        <div>
            <h1>Metadata</h1>
            <ul>
                <li><strong>Date (GMT):</strong> {date_gmt}</li>
                <li><strong>Status:</strong> {status}</li>
                <li><strong>Link:</strong> <a href=\"{link}\">{link}</a></li>
                <li><strong>Author:</strong> {author}</li>
                <li><strong>Author URL:</strong> {author_url}</li>
                <li><strong>Post ID:</strong> {post_id}</li>
                <li><strong>Post link:</strong> <a href\"={post_link}\">{post_link}</a></li>
            </ul>
        </div>
        <div>
            <h1>{author} on {post_title}</h1>
            {content}
        </div>
    </body>
</html>
        """
        buffer = buffer.format(
            author=html.escape(comment["author_name"]),
            author_url=html.escape(comment['author_url']),
            date_gmt=date_gmt.strftime("%d/%m/%Y %H:%M:%S"),
            status=html.escape(comment['status']),
            link=html.escape(comment['link']),
            content=html.escape(comment['content']['rendered']),
            post_title=html.escape(post),
            post_id=int(comment['post']),
            post_link=post_link
        )
        out_file.write(buffer)
        out_file.close()
