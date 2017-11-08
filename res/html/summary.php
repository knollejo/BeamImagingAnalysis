<?php
    $path = "summary/";
    $json = json_decode(file_get_contents($path."data.json"), true);
    $headline = $json["headline"];
    $models = $json["models"];
    $nmodels = count($models);
    $bcids = $json["bcids"];
    $nbcids = count($bcids);
    $names = $json["names"];
    $summaryFields = $json["summaryFields"];
    $summaryFormat = $json["summaryFormat"];
    $summaries = $json["summaries"];
    $nfields = count($summaryFields);

    function print_nav($summaryFields) {
?>
    <p><small>
        <b>Quicklinks:</b>
<?php for($i=0; $i<count($summaryFields); $i++) { ?>
        <a href="#summary<?php echo $i; ?>"><?php echo $summaryFields[$i]; ?></a>,
<?php } ?>
        <a href="#plots">summary plots</a>
    </small></p>
<?php } ?>
<html>
<body>
    <h1><?php echo $headline; ?>: Summary</h1>
    <!-- General results -->
    <?php for($i=0; $i<$nfields; $i++) { ?>
    <h2 id="summary<?php echo $i; ?>">Results: <?php echo $summaryFields[$i]; ?></h2>
    <?php print_nav($summaryFields); ?>
    <table border="1">
        <tr>
            <td></td>
            <td></td>
            <?php foreach($bcids as $bcid) { ?>
            <td><b>BCID <?php echo $bcid; ?></b></td>
            <?php } ?>
        </tr>
    <?php foreach($names as $name) { ?>
        <tr>
            <td rowspan="<?php echo $nmodels; ?>"><b><?php echo $name; ?></b></td>
            <?php $first = True; ?>
    <?php
        for($j=0; $j<$nmodels; $j++) {
            if($first) {
                $first = False;
            } else {
    ?>
        <tr>
    <?php } ?>
            <td><b><?php echo $models[$j]; ?></b></td>
            <?php for($k=0; $k<$nbcids; $k++) { ?>
            <td><?php printf($summaryFormat[$i], $summaries[$summaryFields[$i]][$name][$j][$k][0], $summaries[$summaryFields[$i]][$name][$j][$k][1]); ?></td>
            <?php } ?>
        </tr>
    <?php }} ?>
    </table>
    <?php } ?>
    <!-- Summary plots -->
    <h2 id="plots">Summary plots</h2>
    <?php print_nav($summaryFields); ?>
    <table border="1">
        <?php foreach($names as $name) { ?>
        <tr>
            <td colspan="2" align="center"><b><?php echo $name;?></b><td>
        </tr>
        <tr>
            <td><a href="<?php echo $path . $headline; ?>_chisq_<?php echo $name; ?>.pdf"><img src="<?php echo $path . $headline; ?>_chisq_<?php echo $name; ?>.png" width="100%" /></a></td>
            <td><a href="<?php echo $path . $headline; ?>_corr_<?php echo $name; ?>.pdf"><img src="<?php echo $path . $headline; ?>_corr_<?php echo $name; ?>.png" width="100%" /></a></td>
        </tr>
        <?php } ?>
    </table>
</body>
</html>
