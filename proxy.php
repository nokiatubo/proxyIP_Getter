<?php
// require(dirname(__FILE__).'/include/config.inc.php');

function index()
{
    $mode = $_GET['m'];
    global $db;

    $sql = "SELECT * FROM valid_ip order by score desc";
    $results = $db->query($sql);
    // echo $results

    if (mysql_num_rows($results) > 0) {
        $i = 1;
        while ($fs = $db->fetch_array($results)) {

            $id = $i;
            $ip = $fs["0"];
            $http = $fs["1"];
            $https = $fs["2"];
            $test_times = $fs["3"];
            $failure_times = $fs["4"];
            $response_time = $fs["6"];
            $score = $fs["7"];
            $lastchecktime = $fs["8"];

            $html_str .= "
									<tr class=\"$class\">
										<td>
											$id
										</td>
										<td style=\"word-break:break-all; word-wrap:break-word;\">
											<a href=\"http://$ip\" target=\"_blank\">$ip</a>
										</td>
										<td>
											$http
										</td>
										<td>
											$https
										</td>
										<td>
											$test_times
										</td>
										<td>
											$failure_times
										</td>
										<td>
											$response_time
										</td>
										<td>
											$score
										</td>
										<td>
											$lastchecktime
										</td>
										<td>
											<a href=\"?m=reflush\">刷新</a>|<a href=\"javascript:alert('请以管理员身份登录')\">删除</a>
										</td>
									</tr>\r\n";
            $i++;
        }
        return $html_str;
    }
    else {
        print "";
    }
}
?>