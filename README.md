# SER516-Team-Miami

# Taiga API Integration

This project is built using python for interacting with the Taiga API to perform various task and calculating metrics.

## Clone the repository:

   ```bash
   git clone git@github.com:keer-asu/SER516-Team-Miami.git
   cd SER516-Team-Miami
   ```


## Build and run instructions
1. After cloning the repo, in the root folder:

   On Mac or linux machines, run this command:
   ```bash
   sh start_for_unix_like.sh
   ```
   
   On Windows machines, run this command:
   ```bash
   start_for_windows.bat
   ```

   OR

   Use docker. The command to build and run a docker container is same for Mac, Linux and Windows.
   ```bash
   docker-compose up --build
   ```

## Getting Taiga Project Slug

To interact with the Taiga API using the provided Python script, you will need the project slug of your Taiga project. Follow these steps to find the project slug:

1. **Login to Taiga**: Open your web browser and log in to your Taiga account.

2. **Select the Project**: Navigate to the project for which you want to obtain the project slug.

3. **Project URL**: Look at the URL in your browser's address bar while you are inside the project. The project slug is the part of the URL that comes after the last slash ("/"). For example:
