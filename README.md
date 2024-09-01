![github](https://github.com/user-attachments/assets/575535bb-8470-4682-ad54-d9f086b70f81)
# FCT

(F*ck Corporation Tactics)

A simple Discord user application/bot that lets you download videos from external websites directly to any chat you want.

## Installation

Add it directly to your discord account by using the following link:
https://discord.com/oauth2/authorize?client_id=1279590815827628174
## Demo

Video Demo:

![github](https://github.com/user-attachments/assets/29af2df9-7147-4ceb-aad3-ef24a676a3b6)



# HOSTING

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file or as environment variables to docker

`TOKEN`!

### Optional
For the the bot to run better, add the following environment variables to your .env file or environment variables to docker

`INSTAGRAM_USERNAME`

either 
`INSTAGRAM_PASSWORD` 
or 
`INSTAGRAM_SESSION`(as stringified json of cookies)

## Deployment

### Docker

The preferred way to use this is by using docker, which automatically is synced with the main branch

The docker image link is: `docker.io/kytpbs/FCT`

### Python
To run this project do:

```bash
  python main.py
```

args `main` or `bot` can be given to run using different tokens

## Running Tests

To run tests, you can directly use tox

```bash
  tox
```

or do 
```bash
  pytest .
```

