poetry export -f requirements.txt --output requirements.tmp.txt --without-hashes
sed -E 's/^([a-z0-9\-]*(\[[a-z0-9\-]*\])?==[0-9]+(\.[0-9]+)*) ; python_version >= "3.11" and python_version < "4(.0)?"( and \(?([^\)]*)\)?)?/\1 ; \6/gm;s/^(.*) ; $/\1/gm' requirements.tmp.txt > requirements.txt
rm requirements.tmp.txt
