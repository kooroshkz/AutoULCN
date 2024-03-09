#!/bin/bash

totp=$(oathtool --totp -b <secret_key>)

echo -n $totp | xclip -selection clipboard

exit
