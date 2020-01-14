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

Example 1: change the target

    set target http://example.com

Example 2: add or modify the cookies PHPSESSID and JSESSIONID (because why not?)

    set cookie "PHPSESSID=deadbeef; JSESSIONID=badc0ffee"

### list

Lists specified data from the server.

This command gets data from the server and displays it as a simple list (with no details).

It also can export full scraped data to specified CSV or JSON file (see --csv and --json options). By default, 
WPJsonScraper caches data to avoid requesting the server too often. To get the lastest updates, run this command 
with the --no-cache option.

Use the --limit and --start options to retrieve a subset of all data selected.

When all data is being listed, --csv and --json will append the type to the specified filenames (e.g. mydata-posts.json).

In the case of media files, the files themselves **are not downloaded**.

Example 1: get all posts

    list posts

Example 2: get maximum 10 pages starting at page 15

    list pages --start 15 --limit 10

Example 3: export all listeable content to json files (including for example all-data-posts.json)

    list all --json all-data
