Digital-Ocean-Dynamic-DNS-Updater
=================================

Purpose:
--------
Allows the dynamic updating of an 'A' record that is managed by Digital Oceans domain server.


Liberated From:
---------------
The original script and idea (i.e. the brains behind the whole thing) was lovingly taken from:

    http://pushingkarma.com/notebook/dynamic-dns-your-home-pc-using-digitaloceans-api/

However it was written using Python v2, I had installed v3 so adapted the script as best I could.


Additions:
----------
I then decided it would be cool to also convert it into PHP (I know at least 1 other person that would find it useful)
so that's what I did, enjoy!


Usage:
------
Simply enter your D.O. client credentials at the top of the script. Set the domain you want to update
and the 'Record' for that domain and schedule the script to run however often you want (using for example the Windows
Scheduler or a cron job).

E.g:

My home server has a sticky IP, I want to be able to connect to it remotely using:

    home.joebloggs.com

I'd create an 'A' record in DO with the hostname 'home', under the domain 'joebloggs.co.uk' and while I was there retrieve my API credentials.

If your using the updater.py or updater.php script you'll need a (client ID & key, v1 of the API). If however your using the v2 of the API use updater-v2.php/updater-v2.py (recommended) then you'll need to generate a ['Personal Access Token'](https://cloud.digitalocean.com/settings/applications) with both read and write permission.

Thanks to:
----------
 - @surfer190 , for updatating the original PHP script to use HTTPS
 - @nickwest , for updating the PHP v2 script to interpret paged results
 - @gnoeley , for creating a V2 of the python script
