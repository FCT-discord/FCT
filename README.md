
# FCT

(F*ck Corperation Tactics)

A simple discord user application/bot that lets you download videos from external websites directly to any chat you want.

## Installation

Add it directly to your discord account by using the following link:
https://discord.com/oauth2/authorize?client_id=1279590815827628174
## Demo

Insert gif or link to demo


## Screenshots

![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)


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
To most basically run this project do:

```bash
  python main.py
```

args `main` or `bot` can be given to run using diffrent tokens

## Running Tests

To run tests, you can directly use tox

```bash
  tox
```

or do 
```bash
  pytest .
```

