# WPJsonScraper

## Introduction

![WPJsonScraper capture](doc/WPJsonScraperCapture.png)

WPJsonScraper is a tool for dumping a maximum of the content available on a
WordPress installation. It uses the wp-json API to retrieve all important
information and enumerate every user, post, comment, media and more.

This allows to get information about sensitive files or pages which may be not
protected enough from external access.

## Prerequises

WPJsonScraper is written in Python and should work with any Python 3
environment given that the following packages are installed:

* Python 3
* requests

## Installation

Just clone the repository with git and run `pip install -r requirements.txt`

## Usage

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
* -g, --pages: list all public pages
* -r, --crawl-ns: crawl plugin namespaces for collections. Set it to all to
crawl all namespaces
* --proxy PROXY_URL force the data to pass through a specified proxy server
* --auth CREDENTIALS use the specified credentials as basic HTTP auth for the
server
* --cookies COOKIES add specified Cookies to the requests
* --no-color: remove color (for example to redirect the output to a file)

Moreover, you can export contents of pages and posts to a folder in separate
files:

* --export-pages PAGE_EXPORT_FOLDER
* --export-posts POST_EXPORT_FOLDER

You can set the proxy server with the --proxy flag. It can be an HTTP or HTTPS
as described in Python requests documentation. By default the proxy servers of
the system are used.

Using the -r option, you can crawl collections of the specified namespace. This
allows you to get a set of objects from the API and maybe confidential data ;)

Example:

    http://user:password@example.com:8080/

## Features to implement

WPJsonScraper is not a mature project yet and its features are pretty basic for
the moment. Some of the features that could be implemented in the future are:

* Progress display while retrieving information
* Comments dumping
* Plugins support
* Specific retrievals by id or search options
* Authentication support with NTLM
