#!/bin/bash
echo url="https://www.duckdns.org/update?domains=pi-fitness&token=a87507a7-ad14-4c64-9781-4703824658e8&ip=" | curl -k -o ~/duckdns/duck.log -K -
