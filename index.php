<?php
require(dirname(__FILE__).'/include/config.inc.php');
require(dirname(__FILE__).'/proxy.php');

$mode = $_GET['m'];

$html_str = index();
include('html/index.html');
echo $sitename;
?>