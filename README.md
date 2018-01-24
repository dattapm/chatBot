Technology stack used:
----------------------

The software in this repository has been tested for the following requirements.

1. Python version is 2.x(2.7.5)
2. Only standard libraries have been used and no third-party were used.
3. This code has been tested for proper functionaing on Ubuntu 12.04 OS.
4. The frontend has been tested for proper functioning on Chrome and FireFox browsers.

Isssues found with the lessenger UI:
-----------------------------------
1. Error 204 (NO CONTENT) was not being handled properly by the lessener UI. UI reports a generic message rather than the
   one sent from the backend server.
2. There is a provision to send the response back to the UI in html format(as type 'rich'). But this format has no impact 
   on the UI. UI still displays the html message as normal text.

Some further improvement's that can be made are as follows:
-----------------------------------------------------------
1. Add support for logging module, which wil help in logging to a file at /opt/lessenger,
   which help us in easy debugging and troubleshooting of the issues.
2. Support unicode in user text entries.
3. Add support for user_id checking to make sure that the forecast information that we are sending to is the one who
   has asked for it.
