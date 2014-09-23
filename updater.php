<?php
//Start Configuration
DEFINE('CLIENT_ID', '');    //From Digital Ocean
DEFINE('API_KEY', '');      //From Digital Ocean
DEFINE('DOMAIN', '');       //e.g: joebloggs.co.uk
DEFINE('RECORD', '');       //e.g: home
//End Configuration

DEFINE('CHECK_IP', "http://checkip.dyndns.org:8245");
DEFINE('API_URL', "https://api.digitalocean.com");

$apiCredentials = 'client_id=' . CLIENT_ID . '&api_key=' . API_KEY;

/**
 * Return the contents of a page (DO only uses GET requests for its API...)
 *
 * @param $url string
 *
 * @return mixed
 */
function getWebPage($url)
{
    $ch = curl_init();
    $timeout = 5;
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $timeout);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2);
    $data = curl_exec($ch);
    curl_close($ch);
    return $data;
}

/**
 * Retrieve our external IP address
 *
 * @return mixed
 */
function getExternalIp()
{
    echo 'Fetching external IP from:' . CHECK_IP . "\r\n";
    $html = getWebPage(CHECK_IP);
    if (preg_match('/(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/', $html, $matches) === 0)
    {
        return false;
    }

    return $matches[0];
}

/**
 * Request the domain ID from Digital Ocean, based on its name.
 *
 * @param $apiCredentials string
 *
 * @return bool
 */
function getDomain($apiCredentials)
{
    echo 'Fetching Domain ID for:' . DOMAIN . "\r\n";
    $url = API_URL . '/domains?' . $apiCredentials;
    $json = getWebPage($url);
    $result = json_decode($json, true);

    foreach ($result['domains'] AS $domain)
    {
        if ($domain['name'] === DOMAIN)
        {
            return $domain;
        }
    }

    return false;
}

/**
 * Given the domain ID, fetch all Records and return the one we want.
 *
 * @param $domain array
 * @param $apiCredentials string
 *
 * @return bool
 */
function getRecord($domain, $apiCredentials)
{
    echo 'Fetching Record ID for: ' . RECORD . "\r\n";
    $url = API_URL . '/domains/' . $domain['id'] . '/records?' . $apiCredentials;

    $json = getWebPage($url);
    $result = json_decode($json, true);

    foreach ($result['records'] AS $record)
    {
        if ($record['name'] === RECORD)
        {
            return $record;
        }
    }

    return false;
}

/**
 * Update the DO Domain IP address, providing the IPAddress, the Domain ID and Record ID.
 *
 * @param $record array
 * @param $domain array
 * @param $ipAddress string
 * @param $apiCredentials string
 *
 * @return bool
 */
function setRecordIP($record, $domain, $ipAddress, $apiCredentials)
{
    echo 'Updating record' . $record['name'] . '.' . $domain['name'] . " to " . $ipAddress . "\r\n";
    $url = API_URL . '/domains/' . $domain['id'] . '/records/' . $record['id'] . '/edit?' . $apiCredentials . '&data=' . $ipAddress;
    $json = getWebPage($url);
    $result = json_decode($json, true);
    return $result['status'] === 'OK';
}

try
{
    echo 'Updating ' . RECORD . '.' . DOMAIN . ':' . date('Y-m-d H:i:s') . "\r\n";
    if (($ipAddress = getExternalIp()) === false)
    {
        throw new Exception('Unable to extract external IP address');
    }

    if (($domain = getDomain($apiCredentials)) === false)
    {
        throw new Exception('Unable to find requested domain in DO account');
    }

    if (($record = getRecord($domain, $apiCredentials)) === false)
    {
        throw new Exception('Unable to find requested record in DO account');
    }

    if ($record['data'] === $ipAddress)
    {
        throw new Exception('Record ' . $record['name'] . '.' . $domain['name'] . ' already set to ' . $ipAddress);
    }

    if (setRecordIP($record, $domain, $ipAddress, $apiCredentials) === false)
    {
        throw new Exception('Unable to update IP address');
    }
}
catch (Exception $e)
{
    echo 'Error: ' . $e->getMessage() . "\r\n";
}

