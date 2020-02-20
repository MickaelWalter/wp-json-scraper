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
        Represents the CSV format for format choice
    """

    @staticmethod
    def map_params(el, parameters_to_map):
        """
            Maps params to ids recursively.

            This method automatically maps IDs with the correponding objects given in parameters_to_map. 
            The mapping is made in place as el is passed as a reference.

            :param el: the element that have ID references
            :param parameters_to_map: a dict containing lists of elements to map by ids with el
        """
        for key, value in el.items():
            if key in parameters_to_map.keys() and parameters_to_map[key] is not None:
                if type(value) is int: # Only one ID to map
                    obj = get_by_id(parameters_to_map[key], value)
                    if obj is not None:
                        el[key] = {
                            'id': value,
                            'details': obj
                        }
                elif type(value) is list: # The object is a list of IDs, we map each one
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
            Sets up the right values for a list export.

            This function flattens alist of objects before its serialization in the expected format. 
            It also makes a deepcopy to ensure that the original vlist is not altered.

            :param vlist: the list to prepare for exporting
            :param parameters_to_unescape: parameters to unescape (ex. ["param1", ["param2"]["rendered"]])
            :param parameters_to_map: parameters to map to another (ex. {"param_to_map": param_values_list})
        """
        exported_list = []

        for el in vlist:
            if el is not None:
                # First copy the object
                exported_el = copy.deepcopy(el)
                # Look for parameters to HTML unescape
                for key in parameters_to_unescape:
                    if type(key) is str: # If the parameter is at the root
                        exported_el[key] = html.unescape(exported_el[key])
                    elif type(key) is list: # If the parameter is nested
                        selected = exported_el
                        siblings = []
                        fullpath = {}
                        # We look for the leaf first, not forgetting sibling branches for rebuilding the tree later
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
                        # If we can unescape the parameter, we do it and rebuild the tree starting from the leaf
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
                # If there is any parameter to map, we do it here
                Exporter.map_params(exported_el, parameters_to_map)
                # The resulting element is appended to the list of exported elements
                exported_list.append(exported_el)

        return exported_list

    @staticmethod
    def prepare_filename(filename, fmt):
        """
            Returns a filename with the proper extension according to the given format

            :param filename: the filename to clean
            :param fmt: the file format
            :return: the cleaned filename
        """
        if filename[-5:] != ".json" and fmt == Exporter.JSON:
            filename += ".json"
        elif filename[-4:] != ".csv" and fmt == Exporter.CSV:
            filename += ".csv"
        return filename

    @staticmethod
    def write_file(filename, fmt, csv_keys, data, details=None):
        """
            Writes content to the given file using the given format.

            The key mapping must be a dict of keys or lists of keys to ensure proper mapping.

            :param filename: the path of the file
            :param fmt: the format of the file
            :param csv_keys: the key mapping
            :param data: the actual data to export
            :param details: the details keys to look for
        """
        with open(filename, "w", encoding="utf-8") as f:
            if fmt == Exporter.JSON:
                # The JSON format is straightforward, we dump the flattened objects to JSON
                json.dump(data, f, ensure_ascii=False, indent=4)
            else:
                # The CSV format requires some work, to select the most relevant information
                fieldnames = csv_keys.keys()
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                for el in data:
                    el_csv = {}
                    for key in csv_keys:
                        # First we look for the key specified by csv_keys and select the corresponding leaf
                        k = csv_keys[key]
                        selected = None
                        last_key = None
                        if type(k) is str:
                            last_key = k
                            k = [k] 
                        if k[0] in el.keys():
                            selected = el[k[0]]
                        else:
                            el_csv[key] = ""
                            continue
                        if len(k) > 1:
                            for subkey in k[1:]:
                                if subkey in selected.keys():
                                    selected = selected[subkey]
                                    last_key = subkey
                        # Once the leaf is selected, we verify if there is any kind of ID mapping and act accordingly
                        if type(selected) is dict and 'id' in selected.keys() and 'details' in selected.keys() and last_key in details.keys():
                            el_csv[key] = "%s (%d)" % (selected["details"][details[last_key]], selected["id"])
                        elif type(selected) is not dict and type(selected) is not list:
                            el_csv[key] = selected
                        else:
                            el_csv[key] = "unknown"
                    # And we write the row
                    w.writerow(el_csv)

    @staticmethod
    def export_posts(posts, fmt, filename, tags_list=None, categories_list=None, users_list=None):
        """
            Exports posts in specified format to specified file

            :param posts: the posts to export
            :param fmt: the export format (JSON or CSV)
            :param tags_list: a list of tags to associate them with tag ids
            :param categories_list: a list of categories to associate them with
            category ids
            :param user_list: a list of users to associate them with author id
            :return: the length of the list written to the file
        """
        exported_posts = Exporter.setup_export(posts, 
            [['title', 'rendered'], ['content', 'rendered'], ['excerpt', 'rendered']],
            {
                'author': users_list,
                'categories': categories_list,
                'tags': tags_list,
            })
        
        filename = Exporter.prepare_filename(filename, fmt)
        csv_keys = {
            'id': 'id',
            'date': 'date',
            'modified': 'modified',
            'status': 'status',
            'link': 'link',
            'title': ['title', 'rendered'],
            'author': 'author'
        }
        details = {
            'author': 'name',
        }
        Exporter.write_file(filename, fmt, csv_keys, exported_posts, details)
        return len(exported_posts)

    @staticmethod
    def export_categories(categories, fmt, filename, category_list=None):
        """
            Exports categories in specified format to specified file.

            :param categories: the categories to export
            :param fmt: the export format (JSON or CSV)
            :param filename: the path to the file to write
            :param category_list: the list of categories to be used as parents
            :return: the length of the list written to the file
        """
        exported_categories = Exporter.setup_export(categories, # TODO
            [],
            {
                'parent': category_list,
            })
        
        filename = Exporter.prepare_filename(filename, fmt)

        csv_keys = {
            'id': 'id',
            'name': 'name',
            'post_count': 'count',
            'description': 'description',
            'parent': 'parent'
        }
        details = {
            'parent': 'name'
        }
        Exporter.write_file(filename, fmt, csv_keys, exported_categories, details)
        return len(exported_categories)
    
    @staticmethod
    def export_tags(tags, fmt, filename):
        """
            Exports tags in specified format to specified file

            :param tags: the tags to export
            :param fmt: the export format (JSON or CSV)
            :param filename: the path to the file to write
            :return: the length of the list written to the file
        """
        filename = Exporter.prepare_filename(filename, fmt)
        
        exported_tags = tags # It seems that no modification will be done for this one, so no deepcopy
        csv_keys = {
            'id': 'id',
            'name': 'name',
            'post_count': 'post_count',
            'description': 'description'
        }
        Exporter.write_file(filename, fmt, csv_keys, exported_tags)
        return len(exported_tags)

    @staticmethod
    def export_users(users, fmt, filename):
        """
            Exports users in specified format to specified file.

            :param users: the users to export
            :param fmt: the export format (JSON or CSV)
            :param filename: the path to the file to write
            :return: the length of the list written to the file
        """
        filename = Exporter.prepare_filename(filename, fmt)
        
        exported_users = users # It seems that no modification will be done for this one, so no deepcopy
        csv_keys = {
            'id': 'id',
            'name': 'name', 
            'link': 'link', 
            'description': 'description'
        }
        Exporter.write_file(filename, fmt, csv_keys, exported_users)
        return len(exported_users)

    @staticmethod
    def export_pages(pages, fmt, filename, parent_pages=None, users=None):
        """
            Exports pages in specified format to specified file.
        
            :param pages: the pages to export
            :param fmt: the export format (JSON or CSV)
            :param filename: the path to the file to write
            :param parent_pages: the list of all cached pages, to get parents
            :param users: the list of all cached users, to get users
            :return: the length of the list written to the file
        """
        exported_pages = Exporter.setup_export(pages,
            [["guid", "rendered"], ["title", "rendered"], ["content", "rendered"], ["excerpt", "rendered"]],
            {
                'parent': parent_pages,
                'author': users,
            })
        
        filename = Exporter.prepare_filename(filename, fmt)
        csv_keys = {
            'id': 'id',
            'title': ['title', 'rendered'],
            'date': 'date',
            'modified': 'modified',
            'status': 'status',
            'link': 'link',
            'author': 'author',
            'protected': ['content', 'protected']
        }
        details = {
            'author': 'name'
        }
        Exporter.write_file(filename, fmt, csv_keys, exported_pages, details)
        return len(exported_pages)

    @staticmethod
    def export_media(media, fmt, filename, users=None):
        """
            Exports media in specified format to specified file.

            :param media: the media to export
            :param fmt: the export format (JSON or CSV)
            :param users: a list of users to associate them with author ids
            :return: the length of the list written to the file
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
        
        filename = Exporter.prepare_filename(filename, fmt)
        csv_keys = {
            'id': 'id',
            'title': ['title', 'rendered'],
            'date': 'date',
            'modified': 'modified',
            'status': 'status',
            'link': 'link',
            'author': 'author',
            'media_type': 'media_type'
        }
        details = {
            'author': 'name'
        }
        Exporter.write_file(filename, fmt, csv_keys, exported_media, details)
        return len(exported_media)

    @staticmethod
    def export_namespaces(namespaces, fmt, filename):
        """
            **NOT IMPLEMENTED** Exports namespaces in specified format to specified file.

            :param namespaces: the namespaces to export
            :param fmt: the export format (JSON or CSV)
            :return: the length of the list written to the file
        """
        Console.log_info("Namespaces export not available yet")
        return 0

    # FIXME to be refactored
    @staticmethod
    def export_comments_interactive(comments, fmt, filename, parent_posts=None, users=None):
        """
            Exports comments in specified format to specified file.

            :param comments: the comments to export
            :param fmt: the export format (JSON or CSV)
            :param filename: the path to the file to write
            :param parent_posts: the list of all cached posts, to get parent posts (not used yet because this could be too verbose)
            :param users: the list of all cached users, to get users
            :return: the length of the list written to the file
        """
        exported_comments = Exporter.setup_export(comments,
            [["content", "rendered"]],
            {
                'post': parent_posts,
                'author': users,
            })
        
        # FIXME replacing the post ID by the post title in CSV mode doesn't work yet (nested keys)
        filename = Exporter.prepare_filename(filename, fmt)
        csv_keys = {
            'id': 'id',
            'post': 'post',
            'date': 'date',
            'status': 'status',
            'link': 'link',
            'author': 'author_name',
        }
        details = {
            'post': ['title', 'rendered'] 
        }
        Exporter.write_file(filename, fmt, csv_keys, exported_comments, details)
        return len(exported_comments)

    # TODO deprecated, to be moved to export_posts when HTML will be supported
    @staticmethod
    def export_posts_html(posts, folder, tags_list=None, categories_list=None,
    users_list=None):
        """
            Exports posts as HTML to specified export folder.
        
            :param posts: the posts to export
            :param folder: the export folder
            :param tags_list: a list of tags to associate them with tag ids
            :param categories_list: a list of categories to associate them with category ids
            :param user_list: a list of users to associate them with author id
            :return: the length of the list written to the file
        """
        exported_posts = 0

        date_format = "%Y-%m-%dT%H:%M:%S-%Z"

        if not os.path.isdir(folder):
            os.makedirs(folder)
        for post in posts:
            post_file = None
            if 'slug' in post.keys():
                post_file = open(os.path.join(folder, post['slug'])+".html",
                "wt", encoding="utf-8")
            else:
                post_file = open(os.path.join(folder, str(post['id']))+".html",
                "wt", encoding="utf-8")

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
        out_file = open(os.path.join(export_folder, post, "%04d.html" % comment['id']), "wt", encoding="utf-8")
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
