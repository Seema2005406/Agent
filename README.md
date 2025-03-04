Steps to remotely communicate Agents
--------------------------------------------------------------------------------------------

1. Sign up for ngrok and get your authtoken
Go to ngrok signup page and create an account.
After logging in, get your authtoken from this page.

2. Download and Set Up ngrok on Windows
Download ngrok for Windows:
Go to the ngrok download page and select the Windows version.
Extract the .zip file to a folder of your choice.
Add ngrok to your PATH (optional but recommended):
Right-click on This PC and select Properties.
Click on Advanced system settings on the left, then click Environment Variables.
In the System Variables section, find the Path variable, click Edit, and add the path to the folder where you extracted ngrok (e.g., C:\ngrok).
Click OK to save the changes.

3. Authenticate ngrok
Open a new Command Prompt or PowerShell window.
Run the following command to authenticate ngrok with your account (replace YOUR_AUTHTOKEN with the token you copied earlier):

ngrok authtoken YOUR_AUTHTOKEN

or 

./ngrok authtoken YOUR_AUTHTOKEN

Simple steps which should work:
-------------------------------------------------------------------------------------
1. Sign up for ngrok and get your authtoken
Go to ngrok signup page and create an account.
After logging in, get your authtoken from this page.

2. Install authtoken on powershell
./ngrok authtoken YOUR_AUTHTOKEN

