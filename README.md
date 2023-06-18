
Example of decoding ASK from radiohead.
Pass this to python to decode the payload, and extra data

rtl_433  -R 0 -X "n=radiohead_msgpak,m=OOK_PCM,s=500,l=500,r=2500,preamble=55555551cd" -F mqtt://mqtt:1883 -F kv -vv

time      : 2023-06-18 00:14:31
model     : radiohead_msgpak                       count     : 1             num_rows  : 1             rows      : 
len       : 269          data      : 7162cb2cbb2cb2cc7265c39a55969a56635a2ec65c5b155969aaaac4e4d63563a500
codes     : {269}7162cb2cbb2cb2cc7265c39a55969a56635a2ec65c5b155969aaaac4e4d63563a500

