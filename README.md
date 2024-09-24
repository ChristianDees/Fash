# Fash

![Static Badge](https://img.shields.io/badge/Language-Python-blue)
![GitHub all releases](https://img.shields.io/github/downloads/christiandees/Fash/total)
![GitHub repo size](https://img.shields.io/github/repo-size/christiandees/Fash)

Fash is the **CNU Project's Fake Again SHell**, a lightweight and user-friendly implementation of a POSIX shell inspired by the GNU Project's Bash (Bourne Again SHell). Fash is designed to handle common shell functionalities while providing an intuitive experience for users.


## Table of Contents
1. [Getting Started](#getting-started)
2. [Features](#features)
3. [Libraries](#libraries)
4. [Colaboration](#collaboration)


## Getting Started
To get started with Fash, make sure to have the required modules installed. You can do this by running the following command:

```bash
pip install -r requirements.txt
```
Once the installation is complete, simply execute the application with:
```bash
./main.py
```

Now you can start entering commands. Use `quit` to exit at any time.

## Features
- **User Input Handling**: Efficiently processes user commands and provides feedback.
- **Standard Unix Command Syntax**: Supports familiar command-line syntax for ease of use.
- **Error Management**: Gracefully handles user errors with informative messages.
- **Exit Command**: Type `quit` to safely exit the shell.
- **Directory Navigation**: Use the `cd` command to change directories seamlessly.
- **Input/Output Redirection**: Redirect standard input and output with ease.
- **Piping**: Supports simple command piping for chaining commands together.
- **Background Tasks**: Run processes in the background using the ampersand (`&`).
- **Colored Prompt**: A visually appealing colored prompt enhances the user experience.

## Libraries
Fash is built using only the following libraries:
- **os**: Operating system functionality.
- **sys**: System-specific parameters and functions.
- **re**: Regular expression operations.
- **colorama**: Colored terminal prompt.

## Collaboration
Fash is open to collaboration! We welcome contributions, feedback, and ideas to enhance its functionality and usability. If you're interested in improving Fash, please reach out to the community or contact the creator directly at christianmdees@gmail.com.

Join us in making Fash a powerful and enjoyable shell experience!


