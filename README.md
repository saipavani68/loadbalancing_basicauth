# Project4 - CPSC 449 Web Back-End Engineering - Fall 2020
Guided by Professor: Kenytt Avery @ProfAvery
# Project description: 
In this Project an API Gateway is introduced to mediate between users and the microservices i.e, timelines and users. 
The gateway listens on port 5000 and forward requests to each instance of the correct microservice. We use the round-robin policy for the same. If a request fails with Connection refused or an HTTP Status code in the 500 range,the server is removed from the rotation. Also, Flask Basic-Auth is implemented and the user credentials are validated with the authenticateUser(username, password) API.


The following are the steps to run the project:
1. Clone the github repository https://github.com/nagisettipavani/twitter_alike_apis
2. Install the pip package manager by running the following commands
    > sudo apt update
    
    > sudo apt install --yes python3-pip
   
3. Install Flask by:
    
    > python3 -m pip install Flask python-dotenv
   
4. Run the following commands to install Foreman and HTTPie:
    > sudo apt update
    
    > sudo apt install --yes ruby-foreman httpie

5. Then cd into the gateway folder
    Run the following commands:
    > flask init
    
    > foreman start -m gateway=1,timelines=3,app=3 (Starting an instance of gateway and 3 instances each of timelines and app)


   
