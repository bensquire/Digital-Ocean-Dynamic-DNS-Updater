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
Simply enter your D.O. Client-ID and API-Key at the top of the script you want. Set the domain you want to update
and the 'Record' for that domain and schedule the script to run however often you want (using for example the Windows Scheduler or a cron job).

E.g:

My home server has a sticky IP, I want to be able to connect to it remotely using:

    home.joebloggs.com

I'd create an 'A' record in D.O. with the hostname 'home', under the domain 'joebloggs.co.uk' and while I was there retrieve my API client ID and key.