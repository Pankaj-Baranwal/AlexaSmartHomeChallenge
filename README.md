# AlexaSmartHomeChallenge
Backened of "Where is my sutff" skill on Alexa
The entire Tutorial can be found [here](https://www.hackster.io/crakers/where-s-my-stuff-find-your-misplaced-things-with-alexa-d354e9?ref=challenge&ref_id=105&offset=6).  
In the backend, a python script clicks images of the environment in real time using OpenCV, runs [darknet](https://pjreddie.com/darknet/yolo/) on these frames, classifies the scene into objects identified. Then this information is crossmatched with objects which users usually need finding with, and all this information is stored in a remote database.  
When Alexa is asked about the whereabouts of a particular object, it reaches out to the database and provides users with the last known location of the concerned object!  
  
## Dependencies
Darknet: Installation instructions can be found [here](https://pjreddie.com/darknet/).  
OpenCV 3: A nice and to-the-point detail for installing the latest opencv can be found [here](https://medium.com/@debugvn/installing-opencv-3-3-0-on-ubuntu-16-04-lts-7db376f93961).  
Other dependencies can be installed via requirements.txt  
