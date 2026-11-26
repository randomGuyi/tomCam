# PM290-Deamon

To start the pm290 deamon, enter the following commands: 

```bash
sudo systemctl daemon-reload
sudo systemctl enable pm290-printer.service
sudo systemctl start pm290-printer.service
```

Commands to manage the printer: 
Action	Command
Start connection	sudo systemctl start pm290-printer
Stop connection	sudo systemctl stop pm290-printer
Restart connection	sudo systemctl restart pm290-printer
Check status	sudo systemctl status pm290-printer
View live logs	sudo journalctl -fu pm290-printer
Start automatically at boot	sudo systemctl enable pm290-printer
