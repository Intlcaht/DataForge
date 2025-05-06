#!/bin/sh

# Replace placeholder in index.html with actual API URL
if [ -n "$REACT_APP_API_URL" ]; then
  echo "Injecting REACT_APP_API_URL=$REACT_APP_API_URL"
  sed -i "s|__REACT_APP_API_URL__|$REACT_APP_API_URL|g" /usr/share/nginx/html/index.html
fi

exec "$@"
