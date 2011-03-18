#!/bin/bash

CONUNDRUMENV=/home/dss/conundrum/conundrum.bash

######################################################################
# Modify the following when testing:
#
# RESTARTSERVERS controls whether calls to restart the DSS severs are
# actually made.  1 means servers are restarted, 0 makes this a NOP.
#
# RELEASEHOME is the location of the release code tree
#
# WEBHOME is the location of the second Nell installation, which
# servers the DSS User interface (as opposed to the Scheduler
# interface).
#
# INTEGRATIONHOME is the location of the DSS integration directory

RESTARTSERVERS=0
#RELEASEHOME=/home/dss/release
#WEBHOME=/home/dss.gb.nrao.edu/active/python/
#INTEGRATIONHOME=/home/dss/integration

RELEASEHOME=/home/sandboxes/rcreager/temp/release
WEBHOME=/home/sandboxes/rcreager/temp/release
INTEGRATIONHOME=/home/sandboxes/rcreager/temp/integration

######################################################################


NGNIXPIDFILE=/home/dss/conundrum/logs/nginx.pid
PSQLHOME=/home/dss/conundrum/pgsql
DSSHOST=trent
B="_/"

BLACK="\e[30m"
RED="\e[31m"
GREEN="\e[32m"
ORANGE="\e[33m"
BLUE="\e[34m"
PURPLE="\e[35m"
CYAN="\e[36m"

COLOR=$BLUE
BANNERCOLOR=$RED

print_nell_banner()
{
    printf "$BANNERCOLOR"
    echo "----------------------------------------------------------------------"
    echo ""
    echo "    $B       $B $B$B$B$B $B       $B"
    echo "   $B $B    $B $B       $B       $B"
    echo "  $B   $B  $B $B$B$B   $B       $B"
    echo " $B     $B$B $B       $B       $B"
    echo "$B       $B $B$B$B$B $B$B$B$B $B$B$B$B"
    echo ""
    echo "----------------------------------------------------------------------"
    printf "$BLACK"
}

print_dss_banner()
{
    printf "$BANNERCOLOR"
    echo "----------------------------------------------------------------------"
    echo ""
    echo "    $B$B$B    $B$B$B$B  $B$B$B$B"
    echo "   $B    $B  $B        $B"
    echo "  $B    $B  $B$B$B    $B$B$B"
    echo " $B    $B        $B        $B"
    echo "$B$B$B    $B$B$B$B  $B$B$B$B"
    echo ""
    echo "----------------------------------------------------------------------"
    printf "$BLACK"
}

print_antioch_banner()
{
    printf "$BANNERCOLOR"
    echo "----------------------------------------------------------------------"
    echo ""
    echo "    $B      $B      $B $B$B$B$B $B   $B$B    $B$B$B   $B    $B"
    echo "   $B$B    $B$B    $B    $B    $B $B    $B $B        $B    $B"
    echo "  $B $B   $B  $B  $B    $B    $B $B    $B $B        $B$B$B$B"
    echo " $B$B$B  $B    $B$B    $B    $B $B    $B $B        $B    $B"
    echo "$B   $B $B      $B    $B    $B   $B$B      $B$B$B $B    $B"
    echo ""
    echo "----------------------------------------------------------------------"
    printf "$BLACK"
}

print_weather_banner()
{
    printf "$BANNERCOLOR"
    echo "----------------------------------------------------------------------"
    echo ""
    echo "$B    $B   $B $B$B$B$B $B  $B$B$B$B $B    $B $B$B$B$B $B$B$B"
    echo "$B  $B$B  $B $B       $B$B    $B   $B    $B $B       $B    $B"
    echo "$B $B $B $B $B$B$B   $B $B   $B   $B$B$B$B $B$B$B   $B$B$B$B"
    echo "$B$B  $B$B $B       $B$B$B  $B   $B    $B $B       $B  $B"
    echo "$B    $B  $B$B$B$B $B   $B $B   $B    $B $B$B$B$B $B     $B"
    echo ""
    echo "----------------------------------------------------------------------"
    printf "$BLACK"
}

print_nubbles_banner()
{
    printf "$BANNERCOLOR"
    echo "----------------------------------------------------------------------"
    echo ""
    echo "    $B       $B $B    $B $B$B$B   $B$B$B   $B       $B$B$B$B $B$B$B$B"
    echo "   $B $B    $B $B    $B $B    $B $B    $B $B       $B       $B"
    echo "  $B   $B  $B $B    $B $B$B$B   $B$B$B   $B       $B$B$B   $B$B$B"
    echo " $B     $B$B $B    $B $B    $B $B    $B $B       $B             $B"
    echo "$B       $B $B$B$B$B $B$B$B   $B$B$B   $B$B$B$B $B$B$B$B $B$B$B$B"
    echo ""
    echo "----------------------------------------------------------------------"
    printf "$BLACK"
}

warning()
{
    get_response "\n*** CTRL+C and CTRL+Z keys are disabled. Enter 'q' to quit, or 'c' to continue" "c" "q"

    if test "$?" == "1"
    then
        die 1
    fi
}

die ()
{
    printf "$BLACK"
    exit $1
}

source_dss ()
{
    source $CONUNDRUMENV
}

######################################################################
# get_response
#
# Prints a prompt and obtains a positive or negative response from the
# user.  The prompt is passed in as parameter $1, the expected
# positive response as parameter $2, and the expected negative response
# as parameter $3.  The positive response is the default response
# (i.e., if user enters nothing the positive is assumed.)  The
# responses expected from the user should be alpha characters (a-z)
# and are case insensitive.
#
######################################################################

get_response ()
{
    no_case="`echo $3|tr '[a-z]' '[A-Z]'`"
    yes_case="`echo $2|tr '[a-z]' '[A-Z]'`"
    prompt="$1"

    response="0"

    while test "$response" == "0"
    do
        printf "$COLOR"; printf "$prompt\n"; printf "$BLACK"
        read response
        response="`echo $response|tr '[a-z]' '[A-Z]'`"

        if test "$response" == "$yes_case" -o -z "$response"
        then
            return 0
        elif test "$response" == "$no_case"
        then
            return 1
        else
           response="0"
        fi

    done
}

######################################################################
# check_postgres_server
#
# Tests to see if the PostgreSQL server on $DSSHOST is running, by
# kicking off the psql client in r'run-command and exit' mode,
# specifying the host $DSSHOST.  psql will return 0 if the server was
# there.
#
######################################################################

check_postgres_server ()
{
    psql -U dss -h $DSSHOST --command \\q
    return $?
}

######################################################################
# restart_ngnix
#
# Attempts to restart the ngnix server on $DSSHOST.
#
######################################################################

restart_ngnix()
{
    get_response "Should the NGNIX server be restarted? y/n [n]" "n" "y"

    if test "$?" == "1"
    then
        echo "Restarting NGNIX server..."

        if test "$RESTARTSERVERS" == "1"
        then
            ssh dss@$DSSHOST "source $CONUNDRUMENV; kill `cat $NGNIXPIDFILE`; nginx" 2> /dev/null
        fi
    else
        echo "Skipping NGNIX server restart."
    fi
}

######################################################################
# start_postgres_server
#
# Attempts to restart the PostgreSQL server on $DSSHOST.
#
######################################################################

start_postgres_server()
{
    if test "$RESTARTSERVERS" == "1"
    then
        ssh dss@$DSSHOST "source $CONUNDRUMENV; cd $PSQLHOME; /bin/pg_ctl -D data -l logfile start" 2> /dev/null
    fi
}

######################################################################
# we_not_be_dss
#
# Checks to see if we are not user 'dss'.  This script should be run
# from any user account that is in the dss group but not as user dss.
#
######################################################################

we_not_be_dss()
{
    if test `id -u` -ne `id -u dss`; then
        return 0
    else
        return 1
    fi
}

######################################################################
# save_old_default_settings_file
#
# Saves a copy of the old settings.py.default file in a Nell directory
# to be compared with the incoming one.
#
######################################################################

save_old_default_settings_file ()
{
    OLD_DEFAULT_SETTINGS=`mktemp`
    cp $1/settings.py.default $OLD_DEFAULT_SETTINGS
}

######################################################################
# check_default_settings_file
#
# Compares the new settings.py.default file in a Nell directory to the
# previous one, which has been saved in the '/tmp' directory.
#
######################################################################

check_default_settings_file ()
{
    if test -e $OLD_DEFAULT_SETTINGS
    then
        diff $OLD_DEFAULT_SETTINGS $1/settings.py.default

        if test "$?" == "1"
        then
            echo "settings.py.default has changed, as listed above"
            get_response "Copy and/or edit as appropriate, then press 'c' to continue, or 'q' to quit this script" "c" "q"

            if test "$?" == "1"
            then
                rm $OLD_DEFAULT_SETTINGS
                die 1
            fi
        fi

        rm $OLD_DEFAULT_SETTINGS
    fi
}

######################################################################
# update_release_directory <name>
#
# Updates the named release directory.  The release directory is
# assumed to exist on $RELEASEHOME (such as /home/dss/release).  This
# first tests for modified files.  If it finds any it will print a
# warning and exit the script.  These should be handled manually.
# Next, it fetches the latest from the 'release' branch of integration
# <repository>-bare, lists the changes, and merges them in.
#
######################################################################

update_release_directory()
{
    printf "Updating release directory %s.\n" "$2/$1"
    cd $2/$1
    pwd
    MODIFIED_FILES="1"

    while test "$MODIFIED_FILES" == "1"
    do
        echo "Checking for modified files..."
        MODFILES=`git status --porcelain --untracked-files=no`

        if test -n "$MODFILES"
        then
            printf "%s\n" $MODFILES
            echo "Modified files exist! Please resolve manually before continuing."
            get_response "Press 'c' after fixing, or press 'q' to quit script." "c" "q"

            if test "$?" == "1"
            then
                die 1
            fi
        else
            MODIFIED_FILES="0"
        fi
    done

    echo "No modified files!"
    get_response "Do you wish to pull from integration? y/n [y]" "y" "n"

    if test "$?" == "0"
    then
        echo "Pulling from integration..."
        # fetch and merge is the same as pull.  Using fetch/merge
        # allows the intermediate step of listing the changes that
        # have been fetched.
	git fetch origin release && git log ..origin/release
	git merge origin/release
    fi
}

######################################################################
# check_nell_urls()
#
# Checks to ensure that there is a urls.py and that it is the same as
# urls.py.default.  If not, it will copy urls.py.default to urls.py
#
######################################################################

check_nell_urls()
{
    diff $1/urls.py $1/urls.py.default

    if test ! "$?" == "0"
    then
        echo "'urls.py.default' differes from 'urls.py'. Copy 'urls.py.default' to 'urls.py',"
        echo "then edit 'urls.py'."
        get_response "Press 'c' when done, 'q' to quit this script." "c" "q"

        if test "$?" == "1"
        then
            die 1
        fi
    fi
}

######################################################################
# get_nell_server_pid
#
# Obtains the nell server pid using 'ps'.  Prints out the 'ps' result
# to allow the user to verify it, and stores the PID from the result
# (if the server was running!).  The PID is in the first 5 characters
# from the 'ps' result as invoked here.
#
######################################################################

get_nell_server_pid()
{
    NELLSERVER=`ssh dss@$DSSHOST "ps x | grep 9005 | grep /home/dss/robin/bin/python | grep -v \"grep /home/dss/robin/bin/python\"" 2> /dev/null`
    NELLSERVERPID=`echo $NELLSERVER | head -c 5`

    if test -z "$NELLSERVERPID"
    then
        printf "\nThere does not appear to be a nell server running on %s!\n" "$DSSHOST"
    else
        printf "\nNell server running on %s:\n%s\n" "$DSSHOST" "$NELLSERVER"
    fi
}

######################################################################
# restart_apache
#
# restarts the apache web server on gollum
#
######################################################################

restart_apache()

{
    # Restart Apache on Gollum
    echo "Restarting the Apache server on Gollum"

    if test "$RESTARTSERVERS" == "1"
    then
        ssh root@gollum "/etc/init.d/nrao-apache restart" 2> /dev/null
    fi
}

######################################################################
# stop_apache
#
# restarts the apache web server on gollum
#
######################################################################

stop_apache()

{
    # Restart Apache on Gollum
    echo "Stop the Apache server on Gollum"

    if test "$RESTARTSERVERS" == "1"
    then
        ssh root@gollum "/etc/init.d/nrao-apache stop" 2> /dev/null
    fi
}

######################################################################
# restart_nell
#
# Interactively (re)starts the nell server on $DSSHOST.
#
######################################################################

restart_nell()
{
    get_response "Do you wish to restart the server? y/n [y]" "y" "n"

    if test "$?" == "0"
    then
        stop_nell
        printf "Restarting nell server on %s\n" "$DSSHOST"

        if test "$RESTARTSERVERS" == "1"
        then
            ssh dss@$DSSHOST "source $CONUNDRUMENV; cd $RELEASEHOME/nell; python manage.py runserver 0.0.0.0:9005 </dev/null >~/nell.out 2>&1 &" 2> /dev/null
        fi
    else
        printf "Nell server on %s not restarted.\n" $DSSHOST
        return
    fi

    sleep 2
    get_nell_server_pid
}

######################################################################
# stop_nell
#
# Interactively stops the nell server on $DSSHOST.
#
######################################################################

stop_nell()
{
    get_nell_server_pid

    if test "$1" == "msg"
    then
        get_response "Do you wish to stop the server? y/n [y]" "y" "n"
    fi

    if test "$?" == "0"
    then
        if test ! -z "$NELLSERVERPID"
        then
            printf "Killing current nell server on %s, PID %i\n" "$DSSHOST" $NELLSERVERPID

            if test "$RESTARTSERVERS" == "1"
            then
                ssh dss@$DSSHOST "kill $NELLSERVERPID" 2> /dev/null
            fi
        fi
    fi

    if test "$1" == "msg"
    then
        sleep 2
        get_nell_server_pid
    fi
}

######################################################################
# build_antioch
#
# Builds the antioch source tree.
#
######################################################################

build_antioch()
{
    if test ! -e $RELEASEHOME/antioch/src/Antioch/Settings.lhs
    then
        printf "There is no Settings.lhs in %s/src/Antioch.\n" $RELEASEHOME/antioch
        printf "Please copy one from Settings.lhs.default and edit appropriately\n"
        get_response "Press 'c' when done to continue, or 'q' to quit this script" "c" "q"

        if test "$?" == "1"
        then
            die 1
        fi
    fi

    printf "Building antioch @ %s on %s\n" "$RELEASEHOME/antioch" $DSSHOST
    ssh dss@$DSSHOST "source $CONUNDRUMENV; cd $RELEASEHOME/antioch; make clobber; make"
}

######################################################################
# get_antioch_server_pid
#
# Obtains the PID of the antioch server, if it is running.
#
######################################################################

get_antioch_server_pid()
{
    ANTIOCHSERVER=`ssh dss@$DSSHOST "ps x | grep serve | grep -v grep | grep -v python" 2> /dev/null`
    ANTIOCHSERVERPID=`echo $ANTIOCHSERVER | head -c 5`

    if test -z "$ANTIOCHSERVERPID"
    then
        printf "\nThere does not appear to be an antioch server running on %s!\n" "$DSSHOST"
    else
        printf "\nAntioch server running on %s:\n%s\n" "$DSSHOST" "$ANTIOCHSERVER"
    fi
}

######################################################################
# restart_antioch
#
# Finds the old antioch server and kills it (if it's running) and
# starts a new one.
#
######################################################################

restart_antioch ()
{
    get_response "Do you wish to restart the antioch server? y/n [y]" "y" "n"

    if test "$?" == "0"
    then
        stop_antioch
        printf "Restarting antioch server on %s\n" "$DSSHOST"

        if test "$RESTARTSERVERS" == "1"
        then
            ssh dss@$DSSHOST "source $CONUNDRUMENV; cd $RELEASEHOME/antioch; ./serve </dev/null >~/antioch.out 2>&1 &" 2> /dev/null
        fi
    else
        printf "Antioch server on %s not restarted.\n" $DSSHOST
        return
    fi

    sleep 2
    get_antioch_server_pid
}

######################################################################
# stop_antioch
#
# Finds the old antioch server and kills it (if it's running)
#
######################################################################

stop_antioch ()
{
    get_antioch_server_pid

    if test "$1" == "msg"
    then
        get_response "Do you wish to stop the antioch server? y/n [y]" "y" "n"
    fi

    if test "$?" == "0"
    then
        if test ! -z "$ANTIOCHSERVERPID"
        then
            printf "Killing current antioch server on %s, PID %i\n" "$DSSHOST" $ANTIOCHSERVERPID

            if test "$RESTARTSERVERS" == "1"
            then
                ssh dss@$DSSHOST "kill $ANTIOCHSERVERPID" 2> /dev/null
            fi
        fi
    fi

    if test "$1" == "msg"
    then
        sleep 2
        get_antioch_server_pid
    fi
}

######################################################################
# get_weather_server_pid
#
# obtains the PID for the Cleo weather DB daemon.
#
######################################################################

get_weather_server_pid()
{
    WEATHERSERVER=`ssh dss@$DSSHOST "ps x | grep \"daemonCleoDBImport.py\" | grep -v \"grep\"" 2> /dev/null`
    WEATHERSERVERPID=`echo $WEATHERSERVER | head -c 5`

    if test -z "$WEATHERSERVERPID"
    then
        printf "\nThere does not appear to be a weather server running on %s!\n" "$DSSHOST"
    else
        printf "\nWeather server running on %s:\n%s\n" "$DSSHOST" "$WEATHERSERVER"
    fi
}

######################################################################
# restart_weather
#
# restarts the Cleo weather DB daemon.
#
######################################################################

restart_weather()
{
    get_response "Do you wish to restart the weather server? y/n [y]" "y" "n"

    if test "$?" == "0"
    then
        stop_weather
        printf "Restarting weather server on %s\n" "$DSSHOST"

        if test "$RESTARTSERVERS" == "1"
        then
            ssh dss@$DSSHOST "source $CONUNDRUMENV; cd $RELEASEHOME/antioch/admin; python daemonCleoDBImport.py </dev/null >~/dss_weather.out 2>&1 &" 2> /dev/null
        fi
    else
        printf "Weather server on %s not restarted.\n" $DSSHOST
        return
    fi

    sleep 2
    get_weather_server_pid
}

######################################################################
# stop_weather
#
# restarts the Cleo weather DB daemon.
#
######################################################################

stop_weather()
{
    get_weather_server_pid

    if test "$1" == "msg"
    then
        get_response "Do you wish to stop the weather server? y/n [y]" "y" "n"
    fi

    if test "$?" == "0"
    then
        if test ! -z "$WEATHERSERVERPID"
        then
            printf "Killing current weather server on %s, PID %i\n" "$DSSHOST" $WEATHERSERVERPID

            if test "$RESTARTSERVERS" == "1"
            then
                ssh dss@$DSSHOST "kill $WEATHERSERVERPID" 2> /dev/null
            fi
        fi
    fi

    if test "$1" == "msg"
    then
        sleep 2
        get_weather_server_pid
    fi
}

######################################################################
# update_nubbles
#
# Prompts the user to use eclipse to compile nubbles, then copies the
# results to the release directory.
#
#####################################################################

update_nubbles()
{
    get_response "Please use your Eclipse workspace to compile nubbles, then press 'c' to continue,\nor 'q' to quit this script." "c" "q"

    if test "$?" == "1"
    then
        die 1
    fi

    printf "$COLOR"; printf "Please enter the path to your nubbles sandbox: "; printf "$BLACK"

    while read NUBBLESDIR
    do
        stat $NUBBLESDIR 2>&1 > /dev/null

        if test "$?" == "0"
        then
            if test `basename $NUBBLESDIR` == "nubbles"
            then
                printf "\'%s\' exists, and is a nubbles directory!\n" $NUBBLESDIR
                break
            else
                printf "\'%s\' exists, but does not appear to be a nubbles directory.\n" $NUBBLESDIR
            fi
        fi

        printf "$COLOR"; printf "Please enter the path to your nubbles sandbox: "; printf "$BLACK"
    done

    ssh dss@$DSSHOST "cd $RELEASEHOME/nubbles/war; cp $NUBBLESDIR/war/Nubbles.* .; cp -r $NUBBLESDIR/war/nubbles ." 2> /dev/null
}

######################################################################
# release_nell()
#
# performs the nell portion of the release
#
######################################################################

release_nell()

{
    print_nell_banner
    save_old_default_settings_file $RELEASEHOME/nell
    update_release_directory nell $RELEASEHOME
    check_default_settings_file $RELEASEHOME/nell
    check_nell_urls $RELEASEHOME/nell
    restart_nell

    # now handle the second DSS Nell installation, on the NRAO GB web server
    save_old_default_settings_file $WEBHOME/nell
    update_release_directory nell $WEBHOME
    check_default_settings_file $WEBHOME/nell
    check_nell_urls $WEBHOME/nell
    restart_apache
}

######################################################################
# release_antioch()
#
# performs the antioch portion of the release
#
######################################################################

release_antioch()

{
    print_antioch_banner
    update_release_directory antioch $RELEASEHOME
    build_antioch
    restart_antioch
}

######################################################################
# release_nubbles()
#
# performs the nubbles portion of the release
#
######################################################################

release_nubbles()

{
    print_nubbles_banner
    update_nubbles
}

######################################################################
# print_help()
#
# prints out usage information for the script.
#
######################################################################

print_help()
{
    SCRIPTNAME=`basename $0`
    printf "Usage: $SCRIPTNAME [restart-nell | restart-antioch | restart-weather]\n"
    printf "\tuse $SCRIPTNAME with no command line parameters to effect a complete release.\n"
    printf "\tuse $SCRIPTNAME with one of [restart-nell | restart-antioch | restart-weather\n"
    printf "\t| stop-nell | stop-antioch | stop-weather]"
    printf "\tto restart/start/stop the named service on trent.\n"
}

######################################################################
# main()
#
######################################################################

trap 'warning' SIGINT SIGQUIT SIGTSTP

source_dss

if we_not_be_dss
then
    if test "$1" == "help"
    then
        print_help $0 $1
    elif test "$1" == "restart-nell"
    then
        print_nell_banner
        restart_nell
        restart_apache
    elif test "$1" == "restart-antioch"
    then
        print_antioch_banner
        restart_antioch
    elif test "$1" == "restart-weather"
    then
        print_weather_banner
        restart_weather
    elif test "$1" == "restart-nginx"
    then
        restart_ngnix
    elif test "$1" == "stop-nell"
    then
        print_nell_banner
        stop_nell "msg"
    elif test "$1" == "stop-antioch"
    then
        print_antioch_banner
        stop_antioch "msg"
    elif test "$1" == "stop-weather"
    then
        print_weather_banner
        stop_weather "msg"
    elif test "$1" == "release-nell"
    then
        release_nell
    elif test "$1" == "release-antioch"
    then
        release_antioch
    elif test "$1" == "release-nubbles"
    then
        release_nubbles
    elif test "$1"
    then
        printf "Command-line option '%s' is not recognized by %s\n\n" $1 `basename $0`
        print_help $0 $1
        exit 1
    else
        print_dss_banner

        if check_postgres_server
        then
            printf "Postgres SQL server OK!\n"
        else
            printf "Starting Postgres SQL server on %s\n" $DSSHOST
            start_postgres_server
        fi

        # Restarts ngnix server if directed to.
        restart_ngnix

        # Nell
        release_nell

        # Antioch
        release_antioch

        # Weather
        print_weather_banner
        restart_weather

        # Nubbles
        release_nubbles

        echo "All done!"
        echo "Don't forget to click 'Finish' on the associated release story in Pivotal Tracker!"
    fi
else
    printf "This script should be run under your personal account.  You are\nlogged in as user 'dss'\n"
fi

printf "$BLACK"
