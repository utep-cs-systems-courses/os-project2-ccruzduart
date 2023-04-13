#!/bin/bash
echo -e "\ntesting >\n"
echo -e "Inside Test Scrip\nHello World\nB\nC\nX" > text.txt
cat text.txt
echo -e "\ntesting <\n"
sort < text.txt
echo -e "\ntesting |\n"
cat test.txt | wc
echo -e "\ntesting ls\n"
ls
cd ..
echo -e "\n Changing directories\n"
ls
pwd
