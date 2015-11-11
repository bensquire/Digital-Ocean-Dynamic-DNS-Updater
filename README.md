Digital Ocean Dynamic DNS-Updater
=================================

Purpose:
--------
Allows the dynamic updating of DNS records that are managed by Digital Oceans DNS server.


Liberated From:
---------------
I forked this code from Ben Squires' original project at https://github.com/bensquire/Digital-Ocean-Dynamic-DNS-Updater

He, in turn, improved the original code which came from ['pushingkarma.com'](http://pushingkarma.com/notebook/dynamic-dns-your-home-pc-using-digitaloceans-api/).

Use Case:
------
Given you have a domain whose DNS is hosted with Digital Ocean and wish to dynamically update a domain record based on your current IP, for example, where you have a dynamically assigned IP address from your internet service provider.

This script can be called from a crontab once every 15 minutes, where it detects a change in your IP it will update the record of your choice to point to your new IP address.

For example, I have siftah.net pointing to my current home IP address.

Usage:
------
Get your Personal Access Token from Digital Ocean: ['Personal Access Token'](https://cloud.digitalocean.com/settings/applications).

The PHP script has been designed to be called as a command line tool, or from a crontab. Some config is passed into it in the form of CLI parameters, for example:

> php updater.php accessToken domain record type [command]

were;
1. *accessToken* is your ['Personal Access Token'](https://cloud.digitalocean.com/settings/applications)
2. *domain* is the domain name you want to update (e.g: joebloggs.com).
3. *record* is the value of the a-record you want to update (e.g: home).
4. *type* is the type of record A/CNAME/etc
5. *command* is an optional command which will be called when the IP has been updated. It can be omitted if not required.

Only the fifth parameter is optional, all others are required.

You can also create a cronjob with contents to suit your timing and personal access token:
> */15 * * * * $HOME/scripts/Digital-Ocean-Dynamic-DNS-Updater/updater.php personal_access_token siftah.net @ A [$HOME/scripts/vpnuk_smartdns_client/vpnuk_smartdns_client.php]

Where personal_access_token is your own access token.

config.php
------
I experienced some issues with the IP check page which Bens original script contained, I therefore created my own. If you want to do this you can edit the config.php page to point to your own URL. The regular expression matches any IP address contained in the response, so the format of the page is flexible. You can also use the following PHP snippet;

> <html><head><title>Current IP Check</title></head><body>Current IP Address: <?php
> echo $_SERVER['REMOTE_ADDR'];
> ?></body></html>

Then update the following DEFINE to point to it's URL:
> DEFINE('CHECK_IP', "http://82.196.x.xx/ip.php");


