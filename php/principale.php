<html>
    <head>
    <meta charset="utf-8">
        <link rel="stylesheet" href="style.css" media="screen" type="text/css" />
    </head>
    <body class="neutral">
        <?php
            session_start();
            if (isset($_SESSION['username'])) {
            echo 'Welcome, '.$_SESSION['username']; 
            } else {
            echo 'Sorry, You are not logged in.';
            }
        ?>
    </body>
    <footer>
    <a href="login.php">Logout</a>
    </footer>
</html>