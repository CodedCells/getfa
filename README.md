# getfa
Get Fur Affinity favourites easily

# Functionality
* Uses A & B cookies to access Mature and Adult rated posts
* Configurable to work with and excude pre-downloaded files
* Saves full favourites list, post pages and files

# Quick Start Guide
1. Download the project as ZIP and extract to a folder
2. Create `secret.json` containing your A and B cookies (required to access Mature/Adylt content)
## Find A and B cookies
Chrome: F12 > Application > Storage: Cookies dropdown

Firefox: F12 > Storage > Cookies
## Creating secret.json
Example content:
`{"a": "a_cookie", "b": "b_cookie"}`

## Config
Change `target` to the desired favorites you want.
* Once everything is how you want it, you can just let it run.

# To be implemented
* DDoS Protection notice (it will not work during Cloudflare DDoS protection).
* Options for
** Don't download posts/images
** Dump urls
** No cookies (sfw only)

Feel free to tinker with the code.
