<?php
    $json = json_decode(file_get_contents("nav.json"), true);
    $fill = $json["fill"];
?>
<html>
<head>
    <title>Beam Imaging Results: Fill <?php echo $fill; ?></title>
</head>
<frameset cols="200,*">
    <frame src="navigation.php" name="navigation" />
    <frame name="content" />
</frameset>
</html>
