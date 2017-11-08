<?php
    $modelshort = $_GET["m"];
    if(strpos($_GET["m"], "_") > 0) {
        $modelshort = substr($_GET["m"], 0, strpos($_GET["m"], "_"));
    }
    $bcid = $_GET["c"];
    $path = $_GET["m"] . "/bcid" . $bcid . "/";
    $json = json_decode(file_get_contents($path."data.json"), true);
    $headline = $json["headline"];
    $modelname = $json["modelname"];
    $names = $json["names"];
    $resultFields = $json["resultFields"];
    $results = $json["results"];
    $physicsFields = $json["physicsFields"];
    $physics = $json["physics"];
    $fitFields = $json["fitFields"];
    $fits = $json["fits"];

    function print_nav() {
?>
    <p><small>
        <b>Quicklinks:</b>
        <a href="#results">general results</a>
        <a href="#physics">physics parameters</a>,
        <a href="#fit">fit parameters</a>,
        <a href="#pull">pull distributions</a>,
        <a href="#comb">radial and angular pull distributions</a>
    </small></p>
<?php
    }
?>
<html>
<body>
    <h1><?php echo $headline; ?>: <?php echo $modelname; ?> fit, BCID <?php echo $bcid; ?></h1>
    <!-- General results -->
    <h2 id="results">Results</h2>
    <?php print_nav(); ?>
    <table border="1">
        <tr>
            <td></td>
            <?php foreach($resultFields as $field) { ?>
            <td><b><?php echo $field; ?></b></td>
            <?php } ?>
        </tr>
        <?php foreach($names as $name) { ?>
        <tr>
            <td><b><?php echo $name; ?></b></td>
            <?php foreach($resultFields as $field) { ?>
            <td><?php echo $results[$field][$name]; ?></td>
            <?php } ?>
        </tr>
        <?php } ?>
    </table>
    <!-- Results for physical parameters -->
    <h2 id="physics">Physics parameters</h2>
    <?php print_nav(); ?>
    <table border="1">
        <tr>
            <td></td>
            <?php foreach($physicsFields as $field) { ?>
            <td><b><?php echo $field; ?></b></td>
            <?php } ?>
        </tr>
        <?php foreach($names as $name) { ?>
        <tr>
            <td><b><?php echo $name; ?></b></td>
            <?php foreach($physicsFields as $field) { ?>
            <td><?php echo $physics[$field][$name]; ?></td>
            <?php } ?>
        </tr>
        <?php } ?>
    </table>
    <!-- Results for fit parameters -->
    <h2 id="fit">Fit parameters</h2>
    <?php print_nav(); ?>
    <table border="1">
        <tr>
            <td></td>
            <?php foreach($fitFields as $field) { ?>
            <td><b><?php echo $field; ?></b></td>
            <?php } ?>
        </tr>
        <?php foreach($names as $name) { ?>
        <tr>
            <td><b><?php echo $name; ?></b></td>
            <?php foreach($fitFields as $field) { ?>
            <td><?php echo $fits[$field][$name]; ?></td>
            <?php } ?>
        </tr>
        <?php } ?>
    </table>
    <!-- Plots of pull distributions -->
    <h2 id="pull">Pull distributions</h2>
    <?php print_nav(); ?>
    <table border="1">
        <?php
            foreach($names as $name) {
        ?>
        <tr>
            <td colspan="4" align="center"><b><?php echo $name;?></b><td>
        </tr>
        <tr>
            <?php
                foreach(array("X1", "Y1", "X2", "Y2") as $comp) {
                $plot = $headline . "_res_" . $name . "_" . $modelshort . "_bcid" . $bcid . "_" . $comp;
            ?>
            <td><a href="<?php echo $path . $plot; ?>.pdf"><img src="<?php echo $path . $plot; ?>.png" width="100%" /></a></td>
            <?php } ?>
        </tr>
        <?php } ?>
    </table>
    <!-- Plots of radial pull distributions -->
    <h2 id="comb">Radial and angular pull distributions</h2>
    <?php print_nav(); ?>
    <table border="1">
        <?php
            foreach($names as $name) {
        ?>
        <tr>
            <td colspan="4" align="center"><b><?php echo $name;?></b><td>
        </tr>
        <tr>
            <?php
                foreach(array("X1", "Y1", "X2", "Y2") as $comp) {
                $plot = $headline . "_comb_" . $name . "_" . $modelshort . "_bcid" . $bcid . "_" . $comp;
            ?>
            <td><a href="<?php echo $path . $plot; ?>.pdf"><img src="<?php echo $path . $plot; ?>.png" width="100%" /></a></td>
            <?php } ?>
        </tr>
        <?php } ?>
    </table>
</body>
</html>
