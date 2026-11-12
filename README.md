# Purpose

I have recently found my phone to be more of a distraction than a tool, this project aims first and foremost to offset 
some of my reliance on that device.
To avoid looking at my phone first thing every morning, I developed this project, using a Thermal Printer head and a 
microcontroller, ( + my server), to print a short receipt containing essential daily information. 
In this early stage, that is a summary of the weather, my calendar items, and tasks. 

This project was built in a monorepo, divided into server code, and microcontroller code.

## Server
Calendar data comes from Outlook, which my university will publish (read-only) to a public url as an ics object.
Weather data comes from the open-meteo api
Tasks comes from my Obsidian Vault, shared in a git server.

Managed as a docker service, using Ofelia to schedule the update to the file, which is hosted perpetually.

```
[job-exec "server output updater"]
schedule = 0 3 * * *
container = server-file-server-1
command = python3 src/build_output.py
```

Also requires a cron job to pull changes from Obsidian repo.


## Microcontroller
The earliest version of this code simply connects to the internet on startup, GETs from a url (server), and sends 
the contents to the printer. It then sleeps, but is designed for power to be disconnected until the next use.
