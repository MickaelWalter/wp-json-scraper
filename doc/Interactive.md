# Interactive mode

To help with more complex interactions with WP-JSON API, WPJsonScraper implements an interactive mode.

In interactive mode, the same session is used between requests. So every cookies set by the server and other parameters are kept 
from one request to another.

Typing `command -h` or `command --help` will bring a detailed help message for specific commands.

Tab autocompletes the command name, up and down browse the command history.

## Commands

### help

Lists commands and displays a brief help message about specified commands.

Example 1: display the command list

    help

Example 2: display a brief help message about the command goals.

    help show

### exit

Exits the interactive mode and goes back to the user's shell.

### show

Shows details about global parameters stored in WPJsonScraper memory.

Example: show all parameters

    show all

### set

Sets a specific global parameter. 

Note that in cases of proxy and cookies, the command updates the entries. 
Check the resulting parameter with show if you don't know what that means.

**Note:** changing the target resets the cache but keeps proxies, cookies and authorization headers. Be aware 
of data leakage risks. If you need to keep things apart between targets, relaunch WPJsonScraper or make sure 
all is correctly set up with the `show all` command.

Example 1: change the target

    set target http://example.com

Example 2: add or modify the cookies PHPSESSID and JSESSIONID (because why not?)

    set cookie "PHPSESSID=deadbeef; JSESSIONID=badc0ffee"

### list

Lists specified data from the server.

This command gets data from the server and displays it as a simple list (with no details).

It also can export full scraped data (with all details available) to specified JSON file 
(see --csv and --json options). If a file extension is not specified, WPJsonScraper will append one. 
The export options will try to join data with other API endpoint data (e.g. users with posts). CSV files 
imply that most of the data is removed to ensure human readability. Use this option only to export a list of 
posts.

**Note:** to avoid having too much noise on the target, WPJsonScraper won't fetch automatically any other 
endpoint to complete the exported data. If you want all information to be gathered, you have to build the 
cache first by requesting the data beforehand (for example, getting the user list before exporting the posts).

By default, WPJsonScraper caches data to avoid requesting the server too often. To get the lastest updates, 
run this command with the --no-cache option.

Use the --limit and --start options to retrieve a subset of all data selected.

In the case of media files, the files themselves **are not downloaded**.

Example 1: get all posts

    list posts

Example 2: get maximum 10 pages starting at page 15

    list pages --start 15 --limit 10

Example 3: export all listeable content to json files (including for example all-data-posts.json)

    list all --json all-data

Example 4: list namespaces

    list namespaces

### fetch

Fetches a specific piece of data from the server given its type and its ID. By default, if the data is cached, 
the data is returned from the cache. Use the --no-cache argument to force its retrieval from the server.

The data displayed is more complete than the data displayed by the list command. But some metadata is still not 
displayed. Only the JSON export is a full data dump (with additional mapping when relevant).

**Note:** like in the list function, the data that could complete the displayed information is not automatically 
fetched. You have to get it into cache first or to fetch it separately based on its ID. Moreover, the data 
retrieved by ID is not yet pushed into the cache. It may be in a later version.

Example 1 : display the post with the ID 1

    fetch post 1

Example 2 : display the page with the ID 42 and export it in a JSON file, don't use the cache

    fetch page 42 --no-cache

### search

Looks for data based on the specified keywords. This command doesn't use the cache and systematically uses the 
WordPress API to do searches. One or several object types may be provided to narrow the search scope.

Example 1: look for keyword test in all object types

    search test

Example 2: look for keyword foo in posts and pages

    search --type post --type page foo

Example 3: --limit and --start also work for search results

    search --limit 5 --start 4 bar

### dl

Downloads media based on the provided ID. The ID can be specified as an integer (or list of integers), `all` or 
`cache`. In the first case, only media with the specified IDs will be downloaded. `all` will trigger a fetch from 
the API to list all medias then a download session for each file. `cache` will get media URLs from the cache and 
then download the files. 

Note that if all the IDs specified are in the cache, no lookup will be made on the API. If you want to override 
this behaviour, set the `--no-cache` flag.

Example 1: download the media with the IDs 42 and 63 to the current folder

    dl 42,63 .

Example 2: download all media to user's home folder

    dl all /home/user

Example 3: only media present in the cache (e.g. previously requested with list or fetch) are downloaded

    dl cache .