<?php 
	if (1+1==2) {
		$url = 'localhost:8000/labs?to=263775527640';
		$ch = curl_init($url);
		echo 'tatenda';
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

		$resp = curl_exec($ch);
		curl_close($ch);

		echo $resp;
	}
	?>