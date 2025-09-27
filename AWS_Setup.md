## AWS EC2 

# Local Terminal
After changes are made on app.py
- scp -i "awskeypairname.pem" server.py ec2-user@ec2-18-223-22-108.us-east-2.compute.amazonaws.com:~

**Starts Amazon Linux 2 Server**

# Amazon Linux Terminal
- Bash | $ chmod 400 awskeypairname.pem
- ssh -i "awskeypairname.pem" ec2-user@ec2-18-223-22-108.us-east-2.compute.amazonaws.com

# Web server is up
Web server url:
ec2-user@ec2-18-223-22-108.us-east-2.compute.amazonaws.com:8000
