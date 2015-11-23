<?php 
	if (1+1==2) {
		$url = 'localhost:8000/labs?to=263775527640';
		$ch = curl_init($url);
		curl_setopt($ch, CURLOPT_GET, 1);
		curl_setopt($ch, CURLOPT_POSTFIELDS, '');
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

		$resp = curl_exec($ch);
		curl_close($ch);

		echo $resp;
	}
	?>