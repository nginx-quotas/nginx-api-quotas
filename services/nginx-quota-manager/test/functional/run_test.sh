# -----------------------------------------------------------------------------#
#                                                                              #
#           Running Script for Testing Rate Limiter with Report                #
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
if [ -z "$PYTHONPATH" ] 
then
   export PYTHONPATH=$(PWD)/../../
   echo   $PYTHONPATH
fi

if [ -z "$FUNCTIONAL_TEST_PATH" ] 
then
   export FUNCTIONAL_TEST_PATH=$(PWD)
   echo   $FUNCTIONAL_TEST_PATH
fi

#
# Run functional test cases for the rate limiter.
#
printf "\n"
printf "${YELLOW}+--------------------------------------------------------+\n"
printf "${YELLOW}|                                                        |\n"
printf "${YELLOW}|                    Functional Test                     |\n"
printf "${YELLOW}|                                                        |\n"
printf "${YELLOW}|     (Rate Limiter Client -> Rate Limiter & Bucket)     |\n"
printf "${YELLOW}|                                                        |\n"
printf "${YELLOW}+--------------------------------------------------------+\n"

n=0
test_case_files=`ls $FUNCTIONAL_TEST_PATH/*.py`
for file_name in $test_case_files
do
   let n=$n+1
   printf "\n${GREEN}"
   printf "__________________[ Test Case $n Report ]__________________"
   printf "${NC}\n\n"
   python $file_name
done
