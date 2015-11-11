<?php
/*
If you want to create your own page which returns the IP address,
perhaps with a fixed ip (hosted on Digital Ocean) you can use the
following in a .php page;

<html><head><title>Current IP Check</title></head><body>Current IP Address: <?php
echo $_SERVER['REMOTE_ADDR'];
?></body></html>

Then update the following DEFINE to point to it's URL:
*/
DEFINE('CHECK_IP', "http://checkip.dyndns.org:8245");

//The URL for the API, should not need changing.
DEFINE('API_URL', "https://api.digitalocean.com/v2/");

//Timeout value for accessing the IP page.
DEFINE('CURL_TIMEOUT', 60);
?>
