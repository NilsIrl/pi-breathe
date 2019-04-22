#!/usr/bin/env sh

tr -dc "[:alnum:]" < /dev/urandom | head -c15 | tee src.key

