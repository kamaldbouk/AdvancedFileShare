# Advanced File Sharing System

## Overview

This project is a multithreaded client-server file sharing system developed for my Computer Networks course. It allows users to upload, download, and list files in a distributed environment.
The project supports multiple simultaneous clients and includes features for file integrity verification and logging. It also features a GUI for easy access and a progress bar for visual indication of upload/download progress.
## Core Features

### 1. Client-Server Architecture
A central server hosts and manages shared files. Multiple clients can connect and interact with the server at the same time using multithreading.
### 2. File Operations
Upload: Clients can upload files to the server.
Download: Clients can download files from the server.
List: Clients can view a list of all available files.
### 3. Network Communication
Communication is handled via TCP sockets for reliable transmission.
A text-based protocol is used for the following operations:
UPLOAD
DOWNLOAD
LIST
### 4. File Integrity Checking
Files are verified with hashing mechanisms (SHA-256) after upload/download. This Ensures no file corruption during transmission.
### 5. File Duplicates
Supports versioning (e.g., filename_v2.txt) if a file with the same name exists.
### 6. Logging System
Server-side: Logs client connections, file operations, and errors.
Client-side: Logs file operations and errors.
All logs are stored with timestamps for detailed tracking.

_Refer to the report (Networks_Report.pdf) for more details._
