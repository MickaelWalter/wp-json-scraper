# WPJsonScraper

## Introduction

![WPJsonScraper capture](doc/WPJsonScraperCapture.png)

WPJsonScraper is a tool for dumping a maximum of the content available on a
WordPress installation. It uses the wp-json API to retrieve all important
information and enumerate every user, post, comment, media and more.

This allows to get information about sensitive files or pages which may be not
protected enough from external access.

WPJsonScraper has 2 operation modes: command line arguments and interactive. 
The latest offers a command prompt allowing to do more complex operations on 
the WP-JSON API.

## Prerequises

WPJsonScraper is written in Python and should work with any Python 3
environment given that the following packages are installed:

* Python 3
* requests

## Installation

Just clone the repository with git and run `pip install -r requirements.txt`.

You may want to use a virtualenv for keeping your dependencies consistent across 
Python projects.

## Usage

### Interactive mode

See [Interactive mode](doc/Interactive.md) for more details.

### Command line arguments mode

The tool needs the definition of a target WordPress installation and a flag
instructing which action to do.

You may want to have all available information using the -a flag. But this is
maybe a bit verbose, so you can select which categories of information you need
in these ones :

* -h, --help: display the help and exit
* -v, --version: display the version number and exit
* -a, --all: display all data available
* -i, --info: dump basic information about the target
* -e, --endpoints: dump full endpoint documentation
* -p, --posts: list all published posts
* -u, --users: list all users
* -t, --tags: list all tags
* -c, --categories: list all categories
* -m, --media: list all public media objects
* --download-media MEDIA_FOLDER: download media to the designated folder
* -g, --pages: list all public pages
* -o, --comments: lists comments
* -S, --search SEARCH_TERMS: performs a search on SEARCH_TERMS
* -r, --crawl-ns: crawl plugin namespaces for collections. Set it to all to
crawl all namespaces
* --proxy PROXY_URL force the data to pass through a specified proxy server
* --auth CREDENTIALS use the specified credentials as basic HTTP auth for the
server
* --cookies COOKIES add specified Cookies to the requests
* --no-color: remove color (for example to redirect the output to a file)
* --interactive: start an interactive session

Moreover, you can export contents of pages and posts to a folder in separate
files:

* --export-pages PAGE_EXPORT_FOLDER
* --export-posts POST_EXPORT_FOLDER
* --export-comments COMMENT_EXPORT_FOLDER

You can set the proxy server with the --proxy flag. It can be an HTTP or HTTPS
as described in Python requests documentation. By default the proxy servers of
the system are used.

Example:

    http://user:password@example.com:8080/

Using the -r option, you can crawl collections of the specified namespace. This
allows you to get a set of objects from the API and maybe confidential data ;)

#### Search feature

WordPress WP-JSON API allows to search in posts, pages, media objects, tags, 
categories, comments and users.

The -S (--search) option allows to use this functionnality with 
wp-json-scraper.

It can be used on a specific item type or on several at once.

Examples:

    # Search for "lorem" for all item types specified
    ./WPJsonScraper.py -S lorem https://demo.wp-api.org/
    # Search for "hello world" in posts, users and pages only
    ./WPJsonScraper.py -S "hello world" -p -u -g https://demo.wp-api.org/

## Features to implement

WPJsonScraper is not a mature project yet and its features are pretty basic for
the moment. Some of the features that could be implemented in the future are:

* Posts revisions retrieval
* Plugins support
* Authentication support with NTLM
* WordPress instance save as JSON (limited to the accessible scope) and restore?
* Password-protected content handling
* Support new endpoints added in version 5.0: autosaves, block type, blocks, block_renderer, themes (authenticated access required but WTF?)
* Write tests duh!