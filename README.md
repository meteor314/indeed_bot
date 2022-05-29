<div align="center">  <h1 style="font-size:30px" >indeed-bot <br />  
<img src="https://i.imgur.com/Efe7f9w.png" width="48px" height="48px"> </h1>  </div>  
<p align="center">a tool that applies for you.  
</p>  
<img src="img/indeed.gif" width='100%'>

### How does this work?

This is a python script. It scape indeed.com a and and depending on your chosen parameters, he will be able to apply for you

## Requirements

* **selenium**
* **chromedriver or firefox driver**
* **pip and python3**

If you have aldreay pip installed,  you can just copy and paste this commad :

## Installation

```sh
pip install -r requirements.txt
```

# Configuration ?

You need to configure search options for your profile. You can change this variable directly in main.py.

```python
self.searchOptions = 
{  
	 "q" : "informatique", # domain of search 
	 "l" : "Île-de-France", # Area, For exemple Paris, France 
	 "start" : 0, 
	 # starting page, by default one page contains 10 jobs 
	 "jt" : "apprenticeship", # type of job, trainee, apprenticeship etc... 
	 "end" : 100       
 }  
```

You also need to define your chrome executable and path access. You can find all this information here : **chrome://version**

![Copy your profile path](https://imgur.com/N1WqtcX.pnghttps://i.imgur.com/Qp3GQRk.png)

```python
self.paths = {  
 "profile_path" : "/home/meteor314/.config/google-chrome/Profile 4", 
 "binary_location" :  "/opt/google/chrome/google-chrome-stable", 
 }  
```

***If you launch it for first time, just make sure you 're already connected, don't forget to add your CV on your profile indeed.***

You can find all logs where the bots applies in logs files.

## License

This project is licensed under [MIT](https://raw.githubusercontent.com/meteor314/indeed_bot/master/LICENSE).

### Alert

I am not responsible if your account is banned, you are responsible for your account. The developers of this bot are not responsible for its misuse

#### If you encounter a bug, don't hesitate to open an issue, and any help will be welcome ^_^

Many thanks to [@dalek63](https://github.com/dalek63) for his help, without help, this project would never have got off the ground.
