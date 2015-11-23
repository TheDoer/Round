<?php 
	if (!isempty($_GET['to'])) {
		$to = $_GET['to']
		$url = 'localhost:8000/labs?to='+$to;
		$ch = curl_init($url);
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

		$resp = curl_exec($ch);
		curl_close($ch);

		echo $resp;
	}
	?>