Circus
======
[Docs](https://circus.readthedocs.io/en/latest/)  
[Installation Docs](https://circus.readthedocs.io/en/latest/tutorial/step-by-step/)  

systemd
=======
[Circus and systemd](https://circus.readthedocs.io/en/latest/for-ops/deployment/)  

Production Environment Setup
=====
1. Install Circus
    ```
    sudo apt install libzmq-dev libevent-dev python-dev python-virtualenv
    sudo -H pip3 install circus
    sudo -H pip3 install circus-web
    ```
2. Install Didery
    ```
    pip3 install didery
    ```
3. Create a circus.ini File
    ```
    mkdir /etc/circus/
    vim /etc/circus/circus.ini
    ```
    Paste the contents below into the circus.ini file. Make sure 
    that if you are running multiple instances of Didery that you 
    change the port values for each.
    ```
    [watcher:didery]
    cmd = /usr/local/bin/dideryd -P 8000
    numprocesses = 1
    ```
    Save and quit.
4. Create a systemd service file
    ```
    vim /etc/systemd/system/circus.service
    ```
    Paste the contents below into the circus.service file.
    ```
    [Unit]
    Description=Circus process manager
    After=syslog.target network.target nss-lookup.target
    
    [Service]
    Type=simple
    ExecReload=/usr/local/bin/circusctl reload
    ExecStart=/usr/local/bin/circusd /etc/circus/circus.ini
    Restart=always
    RestartSec=5
    
    [Install]
    WantedBy=default.target
    ```
    Save and quit.
5. Enable the service to startup on boot
    ```
    systemctl enable circus
    ```
6. Start the service
    Restart the systemd Daemon
    ```
    systemctl --system daemon-reload
    ```
    Or You can restart Ubuntu
    ```
    sudo reboot
    ```