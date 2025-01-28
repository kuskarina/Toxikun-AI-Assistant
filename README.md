# Toxikun-AI-Assistant

This project was just trying to find the best AI that can run on a rasberry pi 400 (or CP4, the equivialant)

##This is very system heavy, please be careful of overuse, unless you have a good cooling system on your pi.

first install ollama
```
sudo apt install ollama
```
Then download/run the model to try (There are other models you can try, and if you find a better one please let me know!)

to install the model that is in the code already use this:
```
ollama run qwen2.5:3b
```

There are dependancies, please install those first on your client computer that will handle the communication to the servers
```
pip3 -r requirements.txt
```

then on your raspberry pi or server computer do the same for the PI_4_FILES

edit the script to match your rasperry pi's hostname
or IP
```
ifconfig
hostname -l
```


finally, just run the api.py script, give it a few mins as it might take a minuite to boot up.

then run the client.py script on your client computer!

Profit! $$$

## all code is free, but if you feel up to it, and support my endevors donate $kuskishere
