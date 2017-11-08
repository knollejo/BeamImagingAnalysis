<?php
    $json = json_decode(file_get_contents("nav.json"), true);
    $headline = $json["headline"];
    $models = $json["models"];
    $bcids = $json["bcids"];
?>
<html>
<body>
    <h2><?php echo $headline; ?></h2>
    <p><b><a href="summary.php" target="content">Summary</a></b></p>
    <?php foreach($models as $model) { ?>
    <p><b><?php echo $model[0]; ?></b>
    <ul>
        <?php foreach($bcids as $bcid) { ?>
        <li><a href="page.php?m=<?php echo $model[1]; ?>&c=<?php echo $bcid; ?>" target="content">BCID <?php echo $bcid; ?></a></li>
        <?php } ?>
    </ul></p>
    <?php } ?>
    <p><b>Other Fills</b></p>
    <ul>
    <?php
        $fills = scandir('..');
        $host = "http://" . $_SERVER['HTTP_HOST'] . substr($_SERVER['REQUEST_URI'], 0, -15-strlen($headline));
        foreach($fills as $fill) {
            if(strncmp($fill, "Fill", 4) === 0) {
    ?>
        <li><a href="<?php echo $host . $fill; ?>" target="_parent"><?php echo $fill; ?></a></li>
    <?php }} ?>
    </ul>
</body>
</html>
