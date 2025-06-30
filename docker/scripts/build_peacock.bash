#!/bin/bash

cd /work/peacock
source $NVM_DIR/nvm.sh && \
nvm use 16
node -v && cd vue-components && npm i && npm run build
cd -
cd lang-server && npm i && npm run build
