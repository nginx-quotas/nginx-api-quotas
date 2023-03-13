# -----------------------------------------------------------------------------#
#                                                                              #
#           Running Script for Integration Test with Report                    #
#                                                                              #
# -----------------------------------------------------------------------------#

#
# Common constants.
#
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

#
# Set up environment variables if they are not set up.
#
if [ -z "$INTEGRATION_TEST_PATH" ] 
then
   export INTEGRATION_TEST_PATH=$(PWD)
   echo   $INTEGRATION_TEST_PATH
fi

#
# Run integration test cases for the rate limiter.
#
printf "\n"
printf "${YELLOW}+--------------------------------------------------------+\n"
printf "${YELLOW}|                                                        |\n"
printf "${YELLOW}|                    Integration Test                    |\n"
printf "${YELLOW}|                                         Memory         |\n"
printf "${YELLOW}|                                           |            |\n"
printf "${YELLOW}|  (API Request --> API Gateway <-+-> Rate Limiter App)  |\n"
printf "${YELLOW}|                                 |                      |\n"
printf "${YELLOW}|                                 +-> Fake Upload App    |\n"
printf "${YELLOW}|                                                        |\n"
printf "${YELLOW}+--------------------------------------------------------+\n"

n=0
integration_test_case_files=`ls $INTEGRATION_TEST_PATH/*.go`
for file_name in $integration_test_case_files
do
   let n=$n+1
   printf "\n${GREEN}"
   printf "__________________[ Test Case $n Report ]__________________"
   printf "${NC}\n\n"
   go run $file_name
done
