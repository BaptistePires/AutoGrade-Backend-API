# AutoGrade Backend API
 
 This is the repository for AutoGrade's backend API. You'll find all the steps to follow to 
 set it up on your own computer. 
 
 ## Getting started
 To clone the project : git clone https://gitlab.com/BaptistePires/autograde-backend
 
 ### Prerequisites
 It would be better if your run it on an Linux system because it's and will be working on one.  
 You will need to have a mongoDB Database running on your computer.  
 Python 3.6.x installed 


 
 ### Installing
 After cloning the repository follow those steps  
 They'll be working for a Linux system, if you're running the project on a different system, find
 the equivalent for yours.
 
 Starting the database service :
```shell script
sudo service mongod start
```
Installing pip for python 3.6.x :
```shell script
apt-get install python3-pip 
```
Installing virtualenv using pip3 :
```shell script
pip3 install virtualenv    
```
Then, create an virtual env:
```shell script
virtualenv -p /usr/bin/python3.6 venv
```
Switch to the venv :
```shell script
source venv/bin/activate
```
Download all the python packages needed : 
```shell script
pip3 install -r requirements.txt 
```
Then launch the app :
```shell script
sudo python3 app.py
```
To access to the Swagger GUI, : 127.0.0.1:5000  

To leave it :
```shell script
deactivate
```
 
