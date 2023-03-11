# #!/bin/bash
# red=`tput setaf 1`
# green=`tput setaf 2`
# reset=`tput sgr0`

# printf "\n\n ${green}Building Docker Containers...${reset} \n"
# docker-compose up --build --remove-orphans --detach 


# docker run --rm -it -v /Users/moto/work/lamarr-sm/nuke-lamarr/nuke-config.yml:/home/aws-nuke/config.yml -v ~/.aws:/home/aws-nuke/.aws docker.io/rebuy/aws-nuke --profile nuke-lamarr --config /home/aws-nuke/config.yml
docker run --rm -it -v /Users/moto/work/lamarr-sm/nuke-lamarr/nuke-config.yml:/home/aws-nuke/config.yml -v ~/.aws:/home/aws-nuke/.aws docker.io/rebuy/aws-nuke --profile nuke-lamarr --config /home/aws-nuke/config.yml --no-dry-run