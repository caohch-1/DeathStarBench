#!/usr/bin/env bash

for i in {1..2}; do
  username="username_"$i
  password="password_"$i
  title="Avengers: Endgame"
  text=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 256 | head -n 1)
  curl -d "text="$text"&username="$username"&password="$password"&rating=5&title="$title \
      http://127.0.0.1:8081/wrk2-api/review/compose
done

# for i in {2001..2002}; do
#   curl -d "title=title_"$i"&movie_id=movie_id_"$i \
#       http://127.0.0.1:8081/wrk2-api/movie/register
# done

# for i in {2001..2002}; do
#   curl -d "first_name=first_name_"$i"&last_name=last_name_"$i"&username=username_"$i"&password=password_"$i \
#       http://127.0.0.1:8081/wrk2-api/user/register
# done
 