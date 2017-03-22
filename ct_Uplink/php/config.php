<?php
/**
 * c't Uplink RSS/XML parser configuration file
 * Version 1.1
 * 
 * Customize to your liking.
 * Be careful with the $background option. Enabling this will likely hammer the server.
 * 
 * @author Nils Rekow
 * 
 */
//---------------------------------------------------------------------------------------- CONFIGURATION ----------------------------------------------------------------------------------------
//
$destinationFolder	 = '/home/nrekow/Downloads/ctUplink';			// Destination folder where the downloaded files will be put.
$ua                      =  $_SERVER['HTTP_USER_AGENT']				// Use Browser's user-agent unless empty, then use fallback user-agent.
				? $_SERVER['HTTP_USER_AGENT']
				: 'Mozilla/5.0 (X11; Linux x86_64)';

$url                     = 'http://www.heise.de/ct/uplink/ctuplinkvideohd.rss';	// Source URL of the RSS feed which will be parsed.
$referer                 = $url;						// The referer to send to the server. Default is to use the source URL as referer.

$background              = false;						// Run wget in background. If enabled, will start multiple wget sessions and try to download everything at once.
$logging                 = false;						// Create log file. Defaults to TRUE if running in background is enabled.
$show_only_missing_files = false;						// Show only missing files. If enabled, only files not yet downloaded will be shown.
//
//-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
?>
