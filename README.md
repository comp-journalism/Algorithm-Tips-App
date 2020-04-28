# Algorithm-Tips-App

# Deployment Notes
- To host the server on port 8080 run `waitress-serve --call 'api:create_app' &` 
- In order to serve the API out to the internt configure the AWS server so that it can receive and respond to internet requests by adding an inbound rule for the Security Group of the instance to allow traffic from 0.0.0.0/0 on port 8080