echo $DST_USER
scp -i $KEY ./script/script.py $DST_USER@$DST_HOST:/opt/06script.py
scp -i $KEY ./06script.service $DST_USER@$DST_HOST:/etc/systemd/system/06script.service
ssh -i $KEY $DST_USER@$DST_HOST 'systemctl daemon-reload && systemctl start 06script'
