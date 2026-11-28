#!/bin/sh
# ia_page.sh ARCHIVE_ID N OUT.jpg : download page image n<N> of an archive.org item (retries; archive.org
# sometimes returns a tiny error page). Image numbers are 0-based and do NOT equal printed page numbers:
# always check the page header on the image.
id=$1; n=$2; out=$3
for i in 1 2 3 4; do curl -sSL --max-time 60 "https://archive.org/download/$id/page/n$n.jpg" -o "$out" && [ $(stat -c%s "$out") -gt 5000 ] && exit 0; sleep 3; done; echo FAIL $id $n; exit 1
