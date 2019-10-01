<?php
require(dirname(__FILE__).'/include/config.inc.php');

$mode = $_GET['m'];
global $db;

if ($mode=='') {
	$sql = "SELECT * FROM valid_ip order by score desc";
	$results = $db->query($sql);
	if (mysql_num_rows($results) > 0) {
		$i = 1;
		while ($fs = $db->fetch_array($results))
		{
		    echo $fs["0"];
		    echo '<br>';
		    $i ++;
		}
	} else {
		print "";
	}
} elseif ($mode=='http') {
	$sql = "SELECT * FROM valid_ip where is_http = 1 order by score desc;";
	$results = $db->query($sql);
	if (mysql_num_rows($results) > 0) {
		$i = 1;
		while ($fs = $db->fetch_array($results))
		{
		    echo $fs["0"];
		    echo '<br>';
		    $i ++;
		}
	} else {
		print "";
	}
} elseif ($mode=='https') {
	$sql = "SELECT * FROM valid_ip where is_https = 1 order by score desc";
	$results = $db->query($sql);
	if (mysql_num_rows($results) > 0) {
		$i = 1;
		while ($fs = $db->fetch_array($results))
		{
		    echo $fs["0"];
		    echo '<br>';
		    $i ++;
		}
	} else {
		print "";
	}
} else { }
?>