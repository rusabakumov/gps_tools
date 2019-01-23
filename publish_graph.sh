#!/bin/bash
scp -r viz/$1 ubuntu@52.29.139.162:racestats/
echo "Published to: http://52.29.139.162:8888/$1/graph.html"
