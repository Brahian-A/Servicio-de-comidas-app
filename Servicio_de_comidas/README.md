this is the structure of our app holberton bnb.

hbnb/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       ├── places.py
│   │       ├── reviews.py
│   │       ├── amenities.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── place.py
│   │   ├── review.py
│   │   ├── amenity.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── facade.py
│   ├── persistence/
│       ├── __init__.py
│       ├── repository.py
├── run.py
├── config.py
├── requirements.txt
├── README.md

into the first directory 'app'. we create 4 directories more that contain  the layers involucred in this proyect 'api', 'models', 'service', 'persistence'. also it contain the run file that it's the  in charge of run the startpoint.
the config file is where stand all configs of our app.
the requieriments file where stand the needly tools and dependences for that run allright. and this file, the which contain all information about this project
into the app directory, we have a 4 fundamental pillars. the api, she in charge of the communication with the client, receive and sends status codes http and data. the models, these are the templates we for create all entitys, (user, place, review, amenity). the service, where we implement the facade pattern for the speak beetwen a layer and other. and last, the persistence,  to which store all data handle-in for the app