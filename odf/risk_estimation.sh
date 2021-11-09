for i in {1..1000}; do ./RUN >> output60 2>/dev/null ; echo "$i"; done



./RUN:


#! /bin/bash export SYS_LOG_EVENT=True && python3 -m odf
