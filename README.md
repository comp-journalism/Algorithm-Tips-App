# Algorithm-Tips-App

# Deployment Notes
- In order to serve the API out to the internet configure the AWS server so that it can receive and respond to internet requests by adding an inbound rule for the Security Group of the instance to allow traffic from 0.0.0.0/0 on port 8080
- To host the server on port 8080 of the development server run `python api.py &`. The api should now be accessible via the public IP address of the server. 