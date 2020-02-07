"""
Copyright (c) 2018-2020 Mickaël "Kilawyn" Walter

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
import copy
import html
import json
import csv
from datetime import datetime

from lib.console import Console
from lib.utils import get_by_id

class Exporter:
    """
    Utility functions to export data
    """
    JSON = 1
    """
    Represents the JSON format for format choice
    """
    CSV = 2
    """
    Represents the CSV format fo format choice
    """

    @staticmethod
    def map_params(el, parameters_to_map):
        """
        Maps params to ids recursively
        """
        for key, value in el.items():
            if key in parameters_to_map.keys() and parameters_to_map[key] is not None:
                if type(value) is int:
                    obj = get_by_id(parameters_to_map[key], value)
                    if obj is not None:
                        el[key] = {
                            'id': value,
                            'details': obj
                        }
                elif type(value) is list:
                    vlist = []
                    for v in value:
                        obj = get_by_id(parameters_to_map[key], v)
                        vlist.append(obj)
                    el[key] = {
                        'ids': value,
                        'details': vlist
                    }
            elif value is dict:
                Exporter.map_params(value, parameters_to_map)

    @staticmethod
    def setup_export(vlist, parameters_to_unescape, parameters_to_map):
        """
        Sets up the right values for a list export
        param vlist: the list to prepare for exporting
        param parameters_to_unescape: parameters to unescape (ex. ["param1", ["param2"]["rendered"]])
        param parameters_to_map: parameters to map to another (ex. {"param_to_map": param_values_list})
        """
        exported_list = []

        for el in vlist:
            if el is not None:
                exported_el = copy.deepcopy(el)
                for key in parameters_to_unescape:
                    if type(key) is str:
                        exported_el[key] = html.unescape(exported_el[key])
                    elif type(key) is list:
                        selected = exported_el
                        siblings = []
                        fullpath = {}
                        for k in key:
                            if type(selected) is dict and k in selected.keys():
                                sib = {}
                                for e in selected.keys():
                                    if e != k:
                                        sib[e] = selected[e]
                                selected = selected[k]
                                siblings.append(sib)
                            else:
                                selected = None
                                break
                        if selected is not None and type(selected) is str:
                            selected = html.unescape(selected)
                            key.reverse()
                            fullpath[key[0]] = selected
                            s = len(siblings) - 1
                            for e in siblings[s].keys():
                                fullpath[e] = siblings[s][e]
                            for k in key[1:]:
                                fullpath = {k: fullpath}
                                s -= 1
                                for e in siblings[s].keys():
                                    fullpath[e] = siblings[s][e]
                            key.reverse()
                            exported_el[key[0]] = fullpath[key[0]]
                Exporter.map_params(exported_el, parameters_to_map)
                exported_list.append(exported_el)

        return exported_list

    @staticmethod
    def export_posts(posts, fmt, filename, tags_list=None, categories_list=None, users_list=None):
        """
        Exports posts in specified format to specified file
        param posts: the posts to export
        param fmt: the export format (JSON or CSV)
        param tags_list: a list of tags to associate them with tag ids
        param categories_list: a list of categories to associate them with
        category ids
        param user_list: a list of users to associate them with author id
        """
        exported_posts = Exporter.setup_export(posts, 
            [['title', 'rendered'], ['content', 'rendered'], ['excerpt', 'rendered']],
            {
                'author': users_list,
                'categories': categories_list,
                'tags': tags_list,
            })
        
        if filename[-5:] != ".json" and fmt == Exporter.JSON:
            filename += ".json"
        elif filename[-4:] != ".csv" and fmt == Exporter.CSV:
            filename += ".csv"
        with open(filename, "w", encoding="utf-8") as f:
            if fmt == Exporter.JSON:
                json.dump(exported_posts, f, ensure_ascii=False, indent=4)
            else:
                fieldnames = ['id', 'date', 'modified', 'status', 'link', 'title', 'author']
                w = csv.DictWriter(f, fieldnames=fieldnames)

                w.writeheader()
                for p in exported_posts:
                    csv_post = {
                        'id': p['id'],
                        'date': p['date'],
                        'modified': p['modified'],
                        'status': p['status'],
                        'link': p['link'],
                        'title': p['title']['rendered'],
                    }
                    if 'author' in p.keys() and type(p['author']) is dict and 'details' in p['author'].keys() and 'name' in p['author']['details'].keys():
                        csv_post["author"] = p['author']['details']['name']
                    elif 'author' in p.keys():
                        csv_post["author"] = p['author']
                    else:
                        csv_post["author"] = "unknown"
                    w.writerow(csv_post)
        return len(exported_posts)

    @staticmethod
    def export_categories(categories, fmt, filename, category_list=None):
        """
        Exports categories in specified format to specified file
        param categories: the categories to export
        param fmt: the export format (JSON or CSV)
        param filename: the path to the file to write
        param category_list: the list of categories to be used as parents
        """
        exported_categories = Exporter.setup_export(categories, # TODO
            [],
            {
                'parent': category_list,
            })
        
        if filename[-5:] != ".json" and fmt == Exporter.JSON:
            filename += ".json"
        elif filename[-4:] != ".csv" and fmt == Exporter.CSV:
            filename += ".csv"
        with open(filename, "w", encoding="utf-8") as f:
            if fmt == Exporter.JSON:
                json.dump(exported_categories, f, ensure_ascii=False, indent=4)
            else:
                fieldnames = ['id', 'name', 'post_count', 'description', 'parent']
                w = csv.DictWriter(f, fieldnames=fieldnames)

                w.writeheader()
                for cat in exported_categories:
                    csv_cat = {
                        'id': cat['id'],
                        'name': cat['name'],
                        'post_count': cat['count'],
                        'description': cat['description'],
                        'parent': cat['parent'],
                    }
                    if 'parent' in cat.keys() and type(cat['parent']) is dict and 'details' in cat['parent'].keys() and 'name' in cat['parent']['details'].keys():
                        csv_cat["parent"] = cat['parent']['details']['name']
                    w.writerow(csv_cat)
        return len(exported_categories)
    
    @staticmethod
    def export_tags(tags, fmt, filename):
        """
        Exports tags in specified format to specified file
        param tags: the tags to export
        param fmt: the export format (JSON or CSV)
        param filename: the path to the file to write
        """
        if filename[-5:] != ".json" and fmt == Exporter.JSON:
            filename += ".json"
        elif filename[-4:] != ".csv" and fmt == Exporter.CSV:
            filename += ".csv"
        
        exported_tags = tags # It seems that no modification will be done for this one, so no deepcopy
        with open(filename, "w", encoding="utf-8") as f:
            if fmt == Exporter.JSON:
                json.dump(exported_tags, f, ensure_ascii=False, indent=4)
            else:
                fieldnames = ['id', 'name', 'post_count', 'description']
                w = csv.DictWriter(f, fieldnames=fieldnames)

                w.writeheader()
                for tag in exported_tags:
                    csv_tag = {
                        'id': tag['id'],
                        'name': tag['name'],
                        'post_count': tag['count'],
                        'description': tag['description'],
                    }
                    w.writerow(csv_tag)
        return len(exported_tags)

    @staticmethod
    def export_users(users, fmt, filename):
        """
        Exports users in specified format to specified file
        param users: the users to export
        param fmt: the export format (JSON or CSV)
        param filename: the path to the file to write
        """
        if filename[-5:] != ".json" and fmt == Exporter.JSON:
            filename += ".json"
        elif filename[-4:] != ".csv" and fmt == Exporter.CSV:
            filename += ".csv"
        
        exported_users = users # It seems that no modification will be done for this one, so no deepcopy
        with open(filename, "w", encoding="utf-8") as f:
            if fmt == Exporter.JSON:
                json.dump(exported_users, f, ensure_ascii=False, indent=4)
            else:
                fieldnames = ['id', 'name', 'link', 'description']
                w = csv.DictWriter(f, fieldnames=fieldnames)

                w.writeheader()
                for user in exported_users:
                    csv_user = {
                        'id': user['id'],
                        'name': user['name'],
                        'link': user['link'],
                        'description': user['description'],
                    }
                    w.writerow(csv_user)
        return len(exported_users)

    @staticmethod
    def export_pages(pages, fmt, filename, parent_pages=None, users=None):
        """
        Exports pages in specified format to specified file
        param pages: the pages to export
        param fmt: the export format (JSON or CSV)
        param filename: the path to the file to write
        param parent_pages: the list of all cached pages, to get parents
        param users: the list of all cached users, to get users
        """
        exported_pages = Exporter.setup_export(pages,
            [["guid", "rendered"], ["title", "rendered"], ["content", "rendered"], ["excerpt", "rendered"]],
            {
                'parent': parent_pages,
                'author': users,
            })
        
        if filename[-5:] != ".json" and fmt == Exporter.JSON:
            filename += ".json"
        elif filename[-4:] != ".csv" and fmt == Exporter.CSV:
            filename += ".csv"

        with open(filename, "w", encoding="utf-8") as f:
            if fmt == Exporter.JSON:
                json.dump(exported_pages, f, ensure_ascii=False, indent=4)
            else:
                fieldnames = ['id', 'title', 'date', 'modified', 'status', 'link', 'author', 'protected']
                w = csv.DictWriter(f, fieldnames=fieldnames)

                w.writeheader()
                for page in exported_pages:
                    csv_page = {
                        'id': page['id'],
                        'date': page['date'],
                        'modified': page['modified'],
                        'status': page['status'],
                        'link': page['link'],
                        'title': page['title']['rendered'],
                        'protected': page['content']['protected'],
                    }
                    if 'author' in page.keys() and page['author'] is dict and 'details' in page['author'].keys() and 'name' in page['author']['details'].keys():
                        csv_page['author'] = page['author']['details']['name']
                    else:
                        csv_page['author'] = page['author']
                    w.writerow(csv_page)
        return len(exported_pages)

    @staticmethod
    def export_media(media, fmt, filename, users=None):
        """
        Exports posts in specified format to specified file
        param media: the media to export
        param fmt: the export format (JSON or CSV)
        param users: a list of users to associate them with
        author ids
        """
        exported_media = Exporter.setup_export(media, 
            [
                ['guid', 'rendered'],
                ['title', 'rendered'],
                ['description', 'rendered'],
                ['caption', 'rendered'],
            ],
            {
                'author': users,
            })
        
        if filename[-5:] != ".json" and fmt == Exporter.JSON:
            filename += ".json"
        elif filename[-4:] != ".csv" and fmt == Exporter.CSV:
            filename += ".csv"
        with open(filename, "w", encoding="utf-8") as f:
            if fmt == Exporter.JSON:
                json.dump(exported_media, f, ensure_ascii=False, indent=4)
            else:
                fieldnames = ['id', 'date', 'modified', 'status', 'link', 'title', 'author', 'media_type']
                w = csv.DictWriter(f, fieldnames=fieldnames)

                w.writeheader()
                for m in exported_media:
                    csv_media = {
                        'id': m['id'],
                        'date': m['date'],
                        'modified': m['modified'],
                        'status': m['status'],
                        'link': m['link'],
                        'title': m['title']['rendered'],
                        'media_type': m['media_type']
                    }
                    if 'author' in m.keys() and type(m['author']) is dict and 'details' in m['author'].keys() and 'name' in m['author']['details'].keys():
                        csv_media["author"] = m['author']['details']['name']
                    elif 'author' in m.keys():
                        csv_media["author"] = m['author']
                    else:
                        csv_media["author"] = "unknown"
                    w.writerow(csv_media)
        return len(exported_media)

    # FIXME to be refactored
    @staticmethod
    def export_comments_interactive(comments, fmt, filename, parent_posts=None, users=None):
        """
        Exports comments in specified format to specified file
        param comments: the comments to export
        param fmt: the export format (JSON or CSV)
        param filename: the path to the file to write
        param parent_posts: the list of all cached posts, to get parent posts (not used yet because this could be too verbose)
        param users: the list of all cached users, to get users
        """
        exported_comments = Exporter.setup_export(comments,
            [["content", "rendered"]],
            {
                'post': parent_posts,
                'author': users,
            })
        
        if filename[-5:] != ".json" and fmt == Exporter.JSON:
            filename += ".json"
        elif filename[-4:] != ".csv" and fmt == Exporter.CSV:
            filename += ".csv"

        with open(filename, "w", encoding="utf-8") as f:
            if fmt == Exporter.JSON:
                json.dump(exported_comments, f, ensure_ascii=False, indent=4)
            else:
                fieldnames = ['id', 'post', 'date', 'status', 'link', 'author']
                w = csv.DictWriter(f, fieldnames=fieldnames)

                w.writeheader()
                for comment in exported_comments:
                    csv_comment = {
                        'id': comment['id'],
                        'date': comment['date'],
                        'status': comment['status'],
                        'link': comment['link'],
                    }
                    if 'author' in comment.keys() and comment['author'] is dict and 'details' in comment['author'].keys() and 'name' in comment['author']['details'].keys():
                        csv_comment['author'] = "%s (%d)" % (comment['author']['details']['name'], comment['author']['id'])
                    else:
                        csv_comment['author'] = comment['author_name']
                    if 'post' in comment.keys() and comment['post'] is dict and 'details' in comment['post'].keys() and 'title' in comment['post']['details'].keys():
                        csv_comment['post'] = comment['post']['details']['title']['rendered']
                    else:
                        csv_comment['post'] = comment['post']
                    w.writerow(csv_comment)
        return len(exported_comments)

    @staticmethod
    def export_posts_html(posts, folder, tags_list=None, categories_list=None,
    users_list=None):
        """
        Exports posts as HTML to specified export folder. TODO deprecated, to be moved to export_posts
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
