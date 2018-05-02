#!/usr/bin/env bash
#
# Maloney Episodes Downloader
# Version 1.2.1
#
# Desription
#	Download latest episodes of SRF's "Die haarstäubenden Fälle des Philip Maloney"
#
# Requirements
#	awk
#	curl
#	grep
#	sed
#	wget
#	xmllint
#
# Setup dependencies
#	sudo apt install gawk curl grep sed wget libxml2-utils
#	
# Usage
#	./maloney.sh [destination]
#
#

# Set this to false to generate an XML items list instead of downloading episodes.
download_flag="true"
download_folder="/mnt/d/Downloads/maloney"

if [[ ! -z $1 && -d $1 ]]; then
	download_folder="$1";
fi

echo "Checking for new Philip Maloney episodes ..."
# echo "Using $download_folder"

# Downloads the current item if it's not available in the current folder.
function download_item() {
	title="$1"
	audio_url="$2"
	filesize_B="$3"
	pub_date="$4"
	description="$5"

	if [ ! -d "$download_folder" ]; then
		mkdir "$download_folder"
	fi
	
	if [ ! -f "$download_folder/$pub_date $title.mp3" ]; then
		wget -a maloney.log -nv -c -O "$download_folder/$pub_date $title.mp3" $audio_url
	fi
}


# Generate XML/RSS feed.
function print_podcast_rss() {
	items="$1"

	cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
	<channel>
		<title>Maloney</title>
		<language>de-ch</language>
		<copyright>(c) 2017 SRF</copyright>
		<description>Die haarsträubenden Fälle des Philip Maloney. Wer die Hörspiel-Reihe nicht kennt, hat etwas verpasst.</description>
		<image>
			<title>So geht das!</title>
			<url>https://www.srf.ch/static/radio/modules/dynimages/144/srf-3/00-2015/standardbilder/261957.maloneyneuepg.jpg</url>
		</image>
		$items
	</channel>
</rss>
EOF
}


# Generate XML of a single episode.
function print_item() {
	title="$1"
	audio_url="$2"
	filesize_B="$3"
	pub_date="$4"
	description="$5"

	cat <<EOF
		<item>
			<title>$title</title>
			<enclosure type="audio/mpeg" url="$audio_url" length="$filesize_B" />
			<pubDate>$pub_date</pubDate>
			<description>$description</description>
		</item>
EOF
}


# Initialize variables.
items=""
offset=0
has_episodes="true"
has_new_episodes="false"


# Main loop.
while [ "$has_episodes" = "true" ]; do
	index_url="https://www.srf.ch/sendungen/maloney/layout/set/ajax/Sendungen/maloney/sendungen/(offset)/$offset"
	index=$(curl --silent --compressed "$index_url")

	# Quirks to tell xmllint the input charset.
	index=$(echo $index | sed -e 's/<head>/<head><meta charset="UTF-8">/')


	function xmllint() {
		echo -n $index | /usr/bin/env xmllint --html --xpath "$1" - 2>/dev/null
	}


	episodes_selector="//li[contains(@class, 'episode')]"
	num_episodes=$(xmllint "count($episodes_selector)")

	echo "Found $num_episodes episodes."
	if [ $num_episodes == 0 ]; then
		has_episodes="false"
		break
	fi
	
	for i in $(seq 1 $num_episodes); do
		episode_selector="($episodes_selector)[$i]"

		# Fetches the info for this episode.
		title=$(xmllint "string($episode_selector/descendant::h3/a/text())")
		description=$(xmllint "string($episode_selector/div/p[last()]/text())")
		pub_date=$(date --date @$(xmllint "string($episode_selector/@data-start)") -I)
		urn=$(xmllint "string($episode_selector/descendant::a[@data-urn]/@data-urn)" | \
			sed -e "s/^urn:srf:ais:audio://")

		if [[ "$urn" == "" ]]; then
			# This (and all following) episode is no longer available.
			has_episodes="false"
			break
		fi

		# Trims the title.
		title=$(echo -n $title | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')

		if [ ! -f "$download_folder/$pub_date $title.mp3" ]; then
			has_new_episodes="true"

			>&2 echo -n "Processing \"$title\" ... "
			# Retrieves the audio download link (the https one).
			audio_source=$(curl --silent --compressed \
				"https://il.srgssr.ch/integrationlayer/1.0/ue/srf/audio/play/$urn" | \
				grep -Po "https.*\.mp3" | \
				head -n1)

			# Fetches the audio filesize.
			filesize_B=$(curl --silent --head "$audio_source" | awk '/Content-Length/ { print substr($2, 1, length($2)-1) }')

			if [ "$download_flag" = "true" ]; then
				>&2 echo -n "downloading ... "
				item=$(download_item "$title" "$audio_source" "$filesize_B" "$pub_date" "$description")
				>&2 echo "ok."
			else
				>&2 echo "added to feed."
				item=$(print_item "$title" "$audio_source" "$filesize_B" "$pub_date" "$description")
			fi
			
			items=$(echo -e "$items\n$item")
		fi
		
		# Removes the last progress output.
		# >&2 tput cuu1
		# >&2 tput el
	done

	offset=$(( $offset + $num_episodes ))
	# >&2 echo $offset
done

# Output generated XML/RSS feed.
if [ ! "$download_flag" = "true" ]; then
	print_podcast_rss "$items"
fi

if [ ! "$has_new_episodes" = "true" ]; then
	echo "No new content available, yet."
fi
