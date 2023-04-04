# TA-asciitable
A beautifultable lib wrapper for splunk
https://pypi.org/project/beautifultable/

index="*" 
| head 20 | table _time index host sourcetype
| asciitable maxwidth=200 style=BeautifulTable.STYLE_COMPACT alignment=BeautifulTable.ALIGN_LEFT

options are require=False 
some style are broken
alignment doesn't work 
