<?php
//Start Configuration
DEFINE('ACCESS_TOKEN', '');         //Digital Ocean Personal Access Tokens (read & write)
DEFINE('DOMAIN', '');               //joebloggs.co.uk
DEFINE('RECORD', '');               //home
//End Configuration

DEFINE('CURL_TIMEOUT', 15);
DEFINE('CHECK_IP', "http://checkip.dyndns.org:8245");
DEFINE('API_URL', "https://api.digitalocean.com/v2/");

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
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, CURL_TIMEOUT);
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
    $html = getWebPage(CHECK_IP);
    if (preg_match('/(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/', $html, $matches) === 0)
    {
        return false;
    }

    return $matches[0];
}

/**
 * Given the domain ID, fetch all Records and return the one we want.
 *
 * @return bool
 * @throws Exception
 */
function getRecord($page=null)
{
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, API_URL . 'domains/' . DOMAIN . '/records'.($page != null ? '?page='.$page : ''));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, CURL_TIMEOUT);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array('Authorization: Bearer ' . ACCESS_TOKEN));

    $data = curl_exec($ch);
    curl_close($ch);

    if ($data === false)
    {
        return false;
    }

    $dataJson = json_decode($data, true);
    foreach ($dataJson['domain_records'] AS $record)
    {
        if ($record['name'] === RECORD)
        {
            return $record;
        }
    }
    
    // Recursive call for pages results
    if(isset($dataJson['links']['pages']['next']) && $dataJson['links']['pages']['next'] != '')
    {
	    $page = preg_match('/page=(?<page_number>\d+)/i', $dataJson['links']['pages']['next'], $match);
	    if(isset($match['page_number']) && $match['page_number'] != '')
	    {
		    return getRecord($match['page_number']);
	    }
    }
    
    return false;
}

/**
 * Update the DO Domain IP address, providing the IPAddress, the Domain and Record ID.
 *
 * @param $record
 * @param $ipAddress
 *
 * @return mixed|string
 * @throws Exception
 */
function setRecordIP($record, $ipAddress)
{
    $data = json_encode(array(
        'data' => $ipAddress
    ));

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, API_URL . 'domains/' . DOMAIN . '/records/' . $record['id']);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "PUT");
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, CURL_TIMEOUT);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
            'Authorization: Bearer ' . ACCESS_TOKEN,
            'Content-Type: application/json',
            'Content-Length: ' . strlen($data)
        )
    );

    $data = curl_exec($ch);
    curl_close($ch);
    return ($data !== false);
}

try
{
    echo 'Updating ' . RECORD . '.' . DOMAIN . ': ' . date('Y-m-d H:i:s') . "\r\n";
    echo 'Fetching external IP from: ' . CHECK_IP . "\r\n";
    if (($ipAddress = getExternalIp()) === false)
    {
        throw new Exception('Unable to extract external IP address');
    }

    echo 'Fetching Record ID for: ' . RECORD . "\r\n";
    if (($record = getRecord()) === false)
    {
        throw new Exception('Unable to find requested record in DO account');
    }

    echo 'Comparing ' . $record['data'] . ' to ' . $ipAddress . "\r\n";
    if ($record['data'] === $ipAddress)
    {
        throw new Exception('Record ' . RECORD . '.' . DOMAIN . ' already set to ' . $ipAddress);
    }

    echo 'Updating record ' . $record['name'] . '.' . DOMAIN . " to " . $ipAddress . "\r\n";
    if (setRecordIP($record, $ipAddress) === false)
    {
        throw new Exception('Unable to update IP address');
    }

    echo 'IP Address successfully updated.' . "\r\n";
}
catch (Exception $e)
{
    echo 'Error: ' . $e->getMessage() . "\r\n";
}