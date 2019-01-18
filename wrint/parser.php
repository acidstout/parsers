<?php
/**
 * WRINT parser
 * 
 * Parse posts for podcasts and create a clickable list of links.
 * 
 * @author nrekow
 */


/**
 * Get category id by slug from a WordPress blog using its REST API v2.
 * 
 * @param string $slug
 * @return integer|boolean
 */
function getCategoryIdBySlug($slug = '') {
	if (!empty($slug)) {
		try {
			$json = @file_get_contents('https://wrint.de/wp-json/wp/v2/categories/?slug=' . $slug);
		
			if ($json !== false && !empty($json)) {
				$obj = json_decode($json); // Returns an object, not an array.
				
				if (is_array($obj) && isset($obj[0]) && is_object($obj[0])) {
					if (isset($obj[0]->id) && !empty($obj[0]->id) && is_numeric($obj[0]->id)) {
						return $obj[0]->id;
					}
				}
			}
		} catch (Exception $e) {
			error_log($e->getMessage());
		}
	}
	
	return false;
}


/**
 * Fetch all posts of a given category.
 * 
 * @param number $cat_id
 * @return array|boolean
 */
function getPostsByCategoryId($cat_id = 0) {
	$links = array();
	$json = '';
	$page = 1;
	
	if (is_numeric($cat_id)) {
		do {
			try {
				$json = @file_get_contents('https://wrint.de/wp-json/wp/v2/posts?categories=' . $cat_id . '&per_page=100&page=' . $page);

				if ($json !== false && !empty($json)) {
					$arr = json_decode($json, true); // Returns an array this time.
					
					foreach ($arr as $items) {
						if (isset($items['content']) && isset($items['content']['rendered']) && !empty($items['content']['rendered'])) {
							$tmp = parsePost($items['content']['rendered']);
							if ($tmp) {
								$links[] = $tmp;
							}
						}
					}
					$page++;
				}
			} catch(Exception $e) {
				error_log($e->getMessage());
				break;
			}
		} while($json !== false && !empty($json));
		
		return $links;
	}
	
	return false;
}


/**
 * Parse HTML for an a-tag with a specific class and return its href-value.
 * 
 * @param string $post
 * @return boolean|string
 */
function parsePost($post) {
	libxml_use_internal_errors(true);
	$dom = new DOMDocument;
	
	$dom->loadHTML($post);
	libxml_clear_errors();
	
	// Use XPath to find all nodes with a class attribute of header
	$xp = new DOMXpath($dom);
	$nodes = $xp->query('//a[@class="powerpress_link_d"]');
	
	// Output first item's content
	if (!is_null($nodes->item(0))) {
		$link = $nodes->item(0)->getAttribute('href');
		return (!empty($link)) ? $link : false;
	}
	
	return false;
}


function generateClickableLinks($links) {
	$output = '<!DOCTYPE html><html><head><meta charset="utf-8"/><title>WRINT podcast parser</title><style>body { font-family: sans-serif; } li a {font-family: monospace; }</style></head><body><h1>All WRINT podcasts</h1><p>Sorted descending (e.g. recent one at the top).</p><ul>';
	
	foreach ($links as $link) {
		$output .= '<li><a href="' . $link . '">' . $link . '</a></li>';
	}
	
	$output .= '</ul></body></html>';
	
	return $output;
}

// Get category id by slug (e.g. podcast).
$cat_id = getCategoryIdBySlug('podcast');


// Get all posts with a given category id, parse their content and extract the links to the podcasts.  
$links = getPostsByCategoryId($cat_id);

// Quick and dirty generate clickable links to each podcast file and show them.
echo generateClickableLinks($links);
