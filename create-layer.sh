binary_url="https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-4/wkhtmltox-0.12.6-4.amazonlinux2_lambda.zip"

wget $binary_url -O wkhtmltox-layer.zip

layer_arn=$(aws lambda publish-layer-version --layer-name wkhtmltox --zip-file fileb://wkhtmltox-layer.zip --query 'LayerVersionArn' --output text)
echo "layer_arn is: $layer_arn"
