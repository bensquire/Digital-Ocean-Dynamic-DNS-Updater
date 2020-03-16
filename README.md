I've decided to mark this reposotory as inactive as I simply don't have the skills, time or inclination to maintain the Python script. The PHP is manageable, but that doesn't seem to be what the people want.

For now I'm going to mark this repo as archived; if anyone wants to take it over please get in touch.


Digital Ocean Dynamic DNS-Updater
=================================

Purpose:
--------
Allows the dynamic updating of an 'A' or 'AAAA' record that is managed by Digital Ocean's DNS servers.


Liberated From:
---------------
The original script and idea (i.e. the brains behind the whole thing) were lovingly taken from ['pushingkarma.com'](http://pushingkarma.com/notebook/dynamic-dns-your-home-pc-using-digitaloceans-api/).

However it was written using Python v2, I had installed v3 so adapted the script as best I could. I then decided it would be cool to also convert it into PHP (I know at least 1 other person that would find it useful) so that's what I did, enjoy!


Usage:
------
Provide your API key, the domain you want to update and the 'Record' for that domain and schedule the script to run however
often you want (using, for example, the Windows Scheduler or a cron job).

E.g:

My home server has a sticky IP, I want to be able to connect to it remotely using:

    home.joebloggs.com

I'd create an 'A' record in DO with the hostname 'home', under the domain 'joebloggs.co.uk' and while I was there
retrieve my ['Personal Access Token'](https://cloud.digitalocean.com/settings/applications).


Example Usage:
--------------
The PHP script has been designed to be called as a command line tool. Config is passed into it in the form of CLI parameters, for example:

    php updater.php accessToken domain record recordType

    python updater.py accessToken domain record recordType

where 'accessToken' is your ['Personal Access Token'](https://cloud.digitalocean.com/settings/applications), 'domain' is the domain name you want to update
(e.g: joebloggs.com), 'record' is the value of the record you want to update (e.g: home), and 'recordtype' is either A or AAAA.


Run Continuously / Cron Style:
-----------------------------

You can run this script continuously (every X number of seconds) by calling it:

    # If you wan to run it every 5 minutes
    python updater.py accessToken domain record recordType --run-every 300

This mode is perfect if you want to run inside a Docker container, where there is no cron by default.

    TOKEN={your token}
    DOMAIN={your domain}
    RECORD={your record}
    RTYPE=A
    TIMEOUT=60
    ARGS="$TOKEN $DOMAIN $RECORD $RTYPE --run-every $TIMEOUT"

    docker run \
      -it \
      --rm \
      --name do-ddns-updater \
      -v "$PWD":/usr/src/app \
      -w /usr/src/app \
      python:3 python updater.py $ARGS


Thanks to:
----------
@surfer190, @nickwest, @gnoeley, @ryanwcraig, @c17r, @larroy for adding additional features, testing code and feedback.
