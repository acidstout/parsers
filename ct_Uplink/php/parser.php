<?php
/**
 * c't Uplink RSS/XML parser
 * Version 1.1
 * 
 * Downloads the c't Uplink RSS HD-video feed and generates a list of wget entries
 * which download each video and stores it using the title of the episode as filename.
 * It also creates a log file for each downloaded file.
 * 
 * @author Nils Rekow
 * 
 */

define('DEBUG', false);


// If no spinning icon exists use the hourglass unicode character instead.
if (file_exists('spin.gif')) {
	$icon = '<img src="spin.gif" alt=""/>';
} else {
	$icon = '&nbsp;&#8987;&nbsp;';
}


// Load config file if available. Otherwise fallback to default config.
if (file_exists('config.php')) {
	require_once 'config.php';
} else {
	$destinationFolder		 = '.';
	$ua                      =  $_SERVER['HTTP_USER_AGENT'] ? $_SERVER['HTTP_USER_AGENT'] : 'Mozilla/5.0 (X11; Linux x86_64)';
	$url                     = 'http://www.heise.de/ct/uplink/ctuplinkvideohd.rss';
	$referer                 = $url;
	$background              = false;
	$logging                 = false;
	$show_only_missing_files = false;
}


// Debug mode
if (DEBUG) {
	$sXML     = curl_download_webpage($url);				// Download the XML.
	$oXML     = new SimpleXMLElement($sXML);				// Create SimpleXMLElement object, ...
	$children = $oXML->xpath('child::node()');				// Create array from XML
	error_log(print_r($children, true), 0);					// Dump result into default error log
	die();
}


// AJAX request handler
if (isset($_POST['ajax']) && !empty($_POST['ajax'])) {

	if (isset($_POST['getfilesize']) && !empty($_POST['getfilesize'])) {
		$url = $_POST['getfilesize'];
		$filesize = curl_get_file_size($url);
		if ($filesize > -1) {
			$filesize = round($filesize / (1024 * 1024 * 1024), 2); // Expecting gigabytes, rounded to two decimal digits.
			print $filesize;
		} else {
			print ' ERR! ';
		}
	}
	
	die();
}


// Init some stuff
$ids           = array();
$filelist      = array();
$httpConfig    = array('referer' => $referer, 'user-agent' => $ua, 'run_in_background' => $background, 'enable_logging' => $logging);
$sXML          = curl_download_webpage($url);			// Download the XML.
$oXML          = new SimpleXMLElement($sXML);			// Create a SimpleXMLElement object, ...
$output        = parseXML($oXML, $httpConfig, $icon);		// ... and parse it for videos and return an HTML formatted list.


// Append some Javascript functionality to the generated content.
$output   .= '<script type="text/javascript">
					var totalSize = 0;
					$(function() {
						if ($("#show_only_missing_files").is(":checked")) {';
							foreach ($filelist as $key => $value) {
								if (file_exists($destinationFolder . DIRECTORY_SEPARATOR . $value)) {
									$output .= '$("#file' . $key . '").hide();';
								}
							}
						$output .= '}';

						if ($show_only_missing_files) {
							foreach ($filelist as $key => $value) {
								if (file_exists($destinationFolder . DIRECTORY_SEPARATOR . $value)) {
									$output .= '$("#file' . $key . '").hide();';
								}
							}
							$output .= '$("#show_only_missing_files").prop("checked", true);';
						}
					
					$output .= '
						$("#show_only_missing_files").click(function() {
							if ($(this).is(":checked")) {';
							foreach ($filelist as $key => $value) {
								if (file_exists($destinationFolder . DIRECTORY_SEPARATOR . $value)) {
									$output .= '$("#file' . $key . '").hide();';
								}
							}
							$output .= '	} else {';
							foreach ($filelist as $key => $value) {
								$output .= '$("#file' . $key . '").show();';
							}
							$output .= '	}
						});';

					$output .= '
						var links = ["' . implode('","', $ids) . '"];
						$.each(links, function(i, e) { 
							$.ajax({
								url: "' . $_SERVER['PHP_SELF'] . '",
								type: "post",
								data: "ajax=1&getfilesize=" + e,
								success: function(result) {
									totalSize += parseFloat(result);
									$("#fs" + i).html(result);
									$("#totalSize").html(totalSize.toFixed(2));
								}
							});
						});
					});
				</script>';

				
// Falback to hard-coded template if template.html doesn't exist.
if (!file_exists('template.html')) {
	$template = '<!DOCTYPE html>
				<html>
					<head>
						<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
						<style type="text/css">
							* {font-size:8pt;}
							html, body, textarea {width:100%;height:100%;margin:0;padding:0;border:0;background-color:#fff;color:#000;}
							a {color:#000;font-weight:bold;vertical-align:middle;line-height:14pt;}
							input[type=text], textarea {background-color:#fafafa;}
							input[type=text] {border:1px solid #eee;margin:0 0 0 4px;width:80%;}
							input[type=checkbox] {position:relative;top:2px;cursor:pointer;}
							label {cursor:pointer;}
							table {border:0 none;padding:0;margin:0;width:100%;}
							tr td {width:25%;}
							textarea {color:#555;}
							.content {height:95%;overflow:auto;}
							#left_side ,#right_side {width:50%;}
							#left_side {position:fixed;top:0;left:0;}
							#right_side {position:fixed;top:0;right:0;}
							#actions {position:fixed;bottom:0;left:0;width:100%;height:5%;overflow:hidden;text-align:center;background-color:#fff;border-top:1px solid #ccc;z-index:100;}
						</style>
						<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
						<title>c\'t Uplink RSS-Feed Parser</title>
					</head>
					<body>
						<div id="actions">
							<table>
								<tr>
									<td>Total size: ~<span id="totalSize"></span>GB</td>
									<td><input type="checkbox" id="show_only_missing_files"/> <label for="show_only_missing_files">Show only missing files</label></td>
									<td><button id="generateBatch" type="button">Generate Windows download script</button><br/><a href="http://gnuwin32.sourceforge.net/packages/wget.htm" target="_blank">Get Wget for Windows</a></td>
									<td><button id="generateBash" type="button">Generate Linux bash download script</button><br/><a href="https://www.gnu.org/software/wget/" target="_blank">Wget shoud be part of your Linux distibution.</a></td>
								</tr>
							</table>
						</div>
						{output}
						<script type="text/javascript">
							$(function() {
								// Select all on focus, but allow to release selection on second click.
								$("#wget").on("focus", function() {
									$(this).one("mouseup", function() {
							            $(this).select();
							            return false;
							        }).select();
								});
								
								// Generate Linux bash script
								$("#generateBash").click(function() {
									var wget = $("#wget").val();
									if (wget.indexOf("@echo off") == -1) {
										if (wget.indexOf("#!/bin/bash") == -1) {
											$("#wget").val("#!/bin/bash\n" + wget);
										} else {
											$("#wget").val(wget);
										}
									} else {
										wget = wget.split("@echo off\n");
										$("#wget").val("#!/bin/bash\n" + wget[1]);
									}
								});
				
								// Generate Windows batch script
								$("#generateBatch").click(function() {
									var wget = $("#wget").val();
									if (wget.indexOf("#!/bin/bash") == -1) {
										if (wget.indexOf("@echo off") == -1) {
											$("#wget").val("@echo off\n" + wget);
										} else {
											$("#wget").val(wget);
										}
									} else {
										wget = wget.split("#!/bin/bash\n");
										$("#wget").val("@echo off\n" + wget[1]);
									}
								});
							});
						</script>
					</body>
				</html>';
} else {
	// Read HTML template
	$template = file_get_contents('template.html');
}


// Replace placeholder in template with generated content
$output = str_replace('{output}', $output, $template);


// Output prepared content
ob_start();
header('Content-Type: text/html; charset=utf-8');
echo $output;
ob_end_flush();
die(); 



/**
 * Returns the size of a file without downloading it, or -1 if the file size could not be determined.
 *
 * @param string $url - The location of the remote file to download. Cannot be null or empty.
 * @return integer $result - The size of the file referenced by $url, or -1 if the size could not be determined.
 */
function curl_get_file_size($url) {
	global $ua;
	
	$result = -1;
	$ch = curl_init($url);

	// Issue a HEAD request and follow any redirects.
	curl_setopt($ch, CURLOPT_NOBODY, true);
	curl_setopt($ch, CURLOPT_HEADER, true);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
	curl_setopt($ch, CURLOPT_USERAGENT, $ua);

	$data = curl_exec($ch);
	curl_close($ch);

	// Check response.
	if ($data) {
		$content_length = "unknown";
		$status = "unknown";

		if (preg_match("/^HTTP\/1\.[01] (\d\d\d)/", $data, $matches)) {
			$status = (int)$matches[1];
		}

		if (preg_match("/Content-Length: (\d+)/", $data, $matches)) {
			$content_length = (int)$matches[1];
		}

		// For details see http://en.wikipedia.org/wiki/List_of_HTTP_status_codes
		if ($status == 200 || ($status > 300 && $status <= 308)) {
			$result = $content_length;
		}
	}

	return $result;
}// END: curl_get_file_size()



/**
 * Downloads a webpage without children.
 *  
 * @param string $url
 * @return string $data
 */
function curl_download_webpage($url) {
	$ch = curl_init();
	
	curl_setopt($ch, CURLOPT_URL, $url);
	curl_setopt($ch, CURLOPT_FAILONERROR, true);
	curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
	curl_setopt($ch, CURLOPT_TIMEOUT, 15);
	
	$data = curl_exec($ch);
	//$info = curl_getinfo($ch);	// Get data about the request itself (e.g. HTTP code, ...).
	curl_close($ch);
	
	return $data;
}// END: curl_download_webpage()



/**
 * Removes all kinds of distractions from a given string and returns a cleaned up string.
 * 
 * @param string $title
 * @return string $title
 */
function cleanupTitle($title) {
	$title = trim(str_replace('"', '', $title));						// Remove all double-quotes and trailing spaces if any.

	// Remove the "c't uplink" string from the front. Default title.
	if (strpos($title, "c't uplink") !== false && strpos($title, "c't uplink") == 0) {
		$title = substr($title, 11);
	}
	
	// Remove the "c't Episode" string fromt the front. Only applicable for early episodes.
	if (strpos($title, "c't Episode") !== false && strpos($title, "c't Episode") == 0) {
		$title = substr($title, 12);
	}
	
	// Cleanup title in order to use it as filename.
	$title = str_replace(': ', ' - ', $title);						// Replace double-colon with dash.
	$title = str_replace(' / ', ', ', $title);						// Replace slash with comma.
	$title = mb_ereg_replace("([^\w\s\d\-_~,;\[\]\(\).])", '', $title);			// Replace everything else which doesn't belong in a filename.
	$title = trim($title);									// Remove trailing spaces if any.
	
	return $title;
}// END: cleanupTitle()



/**
 * Parses XML formatted file and returned HTML formatted list.
 * 
 * @param object $oXML - Simple XML object
 * @param array $httpConfig - Array which contains HTTP configuration (e.g. user-agent, ...)
 * @param string $icon - Placeholder icon until filesize is fetched 
 * 
 * @return string - HTML content of parsed data
 */
function parseXML($oXML, $httpConfig, $icon) {
	global $filelist;
	global $ids;
	
	$i = 0;
	
	$out_array = array();
	$wget_commands = array();
	
	foreach ($oXML->channel->item as $oEntry) {
		$title           = $oEntry->title;						// The title of the episode.
		$link            = $oEntry->guid;						// The link to the file we want to download.
		$wget_parameters = '';								// Clear parameters of previous entry.
		
		$filename = cleanupTitle($title);
		
		// Extract extension from URL. Search position of last dot (the one that separates the extension from the filename.
		$extension = substr($link, strrpos($link, '.'));

		// Check if wget should run in background. If no log file is specified, wget will log into wget-log by default.
		if ($httpConfig['run_in_background']) {
			$wget_parameters .= ' --background';
		}

		// Check if log file should be created.
		if ($httpConfig['enable_logging']) {
			$wget_parameters .= ' --output-file="' . $filename . '.log"';
		} else if ($httpConfig['run_in_background']) {
			$wget_parameters .= ' --output-file="' . $filename . '.log"';
		}
		
		// Add default wget parameters.
		$wget_parameters .= ' --continue --timestamping --referer="' . $httpConfig['referer'] . '" --user-agent="' . $httpConfig['user-agent'] . '" --quiet --output-document="' . $filename . $extension . '" ' . $link;
		
		// Add all wget command-lines.
		$wget_commands[$filename] = htmlentities('wget' . $wget_parameters, ENT_QUOTES, 'UTF-8');

		// Prepare output.
		$out_array[$filename] = '<div id="file' . $i . '"><input type="text" title="Click to select episode title." value="' . $filename . $extension . '" class="filename" onfocus="this.select();" onmouseup="return false;" readonly /> '
							  . '<a href="' . $link . '" title="Download ' . $filename . $extension . '" download="' . $filename . $extension . '" target="_blank">~<span id="fs' . $i . '">' . $icon . '</span>GB &#8595;</a><br/></div>';
		
		$filelist[$i] = $filename . $extension;
		$ids[$i] = $link;
		$i++;
	}
	
	krsort($out_array, SORT_NUMERIC);
	krsort($wget_commands, SORT_NUMERIC);
	
	return '<div id="left_side" class="content">' . implode("\n", $out_array) . '</div><div id="right_side" class="content"><textarea readonly wrap="off" id="wget">' . implode("\n", $wget_commands) . '</textarea></div>';
}// END: parseXML()
?>
