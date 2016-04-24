if [ "$1" == "development" -o "$1" == "testing" ]; then
  export GIMMEJSON_SETTINGS=$1
  echo "switched to $1"
else
  echo "no such environment"
fi
