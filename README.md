# AWS Lambda to convert html to pdf

## Requirements

- [ ] aws-cli is installed
- [ ] aws-cli is configured
- [ ] serverless is setup (https://www.serverless.com/framework/docs/getting-started)

```sh
# create layer
./create-layer.sh
```

1. Make a note of layer created.
2. update the serverless.yml with layer arn.
3. create .env 

```sh
npm i
npm i serverless -g
serverless deploy
```
